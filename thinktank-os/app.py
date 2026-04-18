"""
Think Tank OS - Web Application
Backend API Server
Uses Groq for fast, free AI analysis
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import requests
import io
import re
import os
import time
from urllib.parse import urlparse
import traceback

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)
CORS(app)

# Get Groq API key from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Use fastest Groq model
GROQ_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"

STRATEGIC_PROMPT = """You are a multidisciplinary strategic think tank: economist, systems engineer, and venture capitalist.

Analyze the consulting report below for NON-OBVIOUS 'boring' asset-based business opportunities.

Focus on:
1. Structural Inefficiencies
2. Incentive Misalignments  
3. Underserved Micro-Niches
4. Regulatory Blind Spots

Target sectors: Fleet, logistics, healthcare infrastructure, equipment leasing.

For each opportunity use EXACTLY this format:

---OPPORTUNITY [number]---
HOOK: [punchy social-media-ready sentence]
THE GAP: [2-3 sentences on the market inefficiency]
WHY NOW: [recent catalyst]
ASSET PLAY: [physical assets needed]
BARRIER: [what protects this business]
CAPITAL: [rough investment range]
UNCLE RHEMA ANGLE: [content positioning idea]
---END---

Give exactly 3 opportunities.

REPORT:
{text}

ANALYSIS:"""


# ─────────────────────────────────────────────────────────
# PDF EXTRACTION
# ─────────────────────────────────────────────────────────

def clean_text(text):
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    lines = [ln for ln in text.split('\n') if not ln.strip().isdigit()]
    return '\n'.join(lines).strip()


def extract_from_bytes(raw_bytes):
    """Try multiple methods to extract text from PDF bytes."""
    text = ""
    
    # Method 1: pdfplumber
    if pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
                text = "\n".join(pages)
            if len(text.strip()) > 150:
                return clean_text(text)
        except Exception:
            text = ""
    
    # Method 2: PyPDF2
    if PyPDF2 is not None:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes), strict=False)
            pages = [p.extract_text() for p in reader.pages if p.extract_text()]
            text = "\n".join(pages)
            if len(text.strip()) > 150:
                return clean_text(text)
        except Exception:
            text = ""
    
    # Method 3: Raw byte scrape
    try:
        decoded = raw_bytes.decode("latin-1", errors="ignore")
        chunks = re.findall(r"BT(.*?)ET", decoded, re.DOTALL)
        text = " ".join(chunks)
        text = "".join(c if 32 <= ord(c) < 127 else " " for c in text)
        text = re.sub(r" {2,}", " ", text).strip()
        if len(text.strip()) > 150:
            return clean_text(text)
    except Exception:
        pass
    
    raise ValueError("Could not extract text from PDF")


def scrape_html_text(html_bytes, base_url):
    """Extract text from HTML page, looking for PDF links first."""
    try:
        html = html_bytes.decode("utf-8", errors="ignore")
    except Exception:
        html = html_bytes.decode("latin-1", errors="ignore")
    
    # Look for PDF link
    pdf_links = re.findall(r'href=["\']+([^"\']*\.pdf[^"\']*)["\']+ ', html, re.IGNORECASE)
    if pdf_links:
        from urllib.parse import urljoin
        pdf_url = urljoin(base_url, pdf_links[0])
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(pdf_url, headers=headers, timeout=45)
            if resp.status_code == 200:
                return extract_from_bytes(resp.content)
        except Exception:
            pass
    
    # Scrape HTML text
    html = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>",
                  " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    if len(text.strip()) > 300:
        return clean_text(text)
    
    raise ValueError("Could not extract enough content from webpage")


def fetch_from_url(url):
    """Download and extract text from URL (PDF or HTML)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/pdf,*/*"
    }
    
    resp = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
    
    if resp.status_code != 200:
        raise ValueError(f"Server returned HTTP {resp.status_code}")
    
    content_type = resp.headers.get("Content-Type", "")
    
    # Direct PDF
    if "pdf" in content_type or url.lower().split("?")[0].endswith(".pdf"):
        return extract_from_bytes(resp.content)
    
    # HTML page
    if "html" in content_type or url.endswith((".html", ".htm")):
        return scrape_html_text(resp.content, url)
    
    # Unknown - try as PDF
    try:
        return extract_from_bytes(resp.content)
    except Exception:
        raise ValueError("Could not process file at this URL")


# ─────────────────────────────────────────────────────────
# GROQ API
# ─────────────────────────────────────────────────────────

def analyze_with_groq(report_text):
    """Send text to Groq for analysis."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set. Add it to environment variables.")
    
    # Trim to 4000 chars
    trimmed = report_text[:4000]
    prompt = STRATEGIC_PROMPT.format(text=trimmed)
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strategic business analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        "status": "online",
        "ai": "groq",
        "model": GROQ_MODEL,
        "has_api_key": bool(GROQ_API_KEY)
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a report from URL or uploaded file.
    
    Request:
        - url: PDF URL (optional)
        - file: uploaded PDF file (optional)
    
    Response:
        - success: bool
        - insights: str (analysis)
        - error: str (if failed)
    """
    try:
        # Check for URL
        data = request.get_json() if request.is_json else {}
        url = data.get('url', '').strip() if data else None
        
        # Check for uploaded file
        uploaded_file = request.files.get('file')
        
        if not url and not uploaded_file:
            return jsonify({"error": "No URL or file provided"}), 400
        
        # Extract text
        if uploaded_file:
            raw_bytes = uploaded_file.read()
            text = extract_from_bytes(raw_bytes)
            source = uploaded_file.filename
        else:
            text = fetch_from_url(url)
            source = url
        
        if len(text) < 100:
            return jsonify({"error": "Extracted text too short"}), 400
        
        # Analyze with Groq
        insights = analyze_with_groq(text)
        
        return jsonify({
            "success": True,
            "insights": insights,
            "source": source,
            "text_length": len(text)
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
