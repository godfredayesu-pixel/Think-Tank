# 🧠 Think Tank OS - Web Application

Strategic Intelligence Arbitrage System powered by Groq AI.

## 🚀 Quick Deploy to Render (5 Minutes)

### Step 1: Get a Groq API Key (Free)

1. Go to https://console.groq.com
2. Sign up (it's free)
3. Click "API Keys" in the sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

**Keep this key safe - you'll need it in Step 3!**

---

### Step 2: Upload Code to GitHub

1. Go to https://github.com/new
2. Name your repo: `thinktank-os`
3. Make it Public or Private (your choice)
4. Click "Create repository"
5. Upload all these files:
   - `app.py`
   - `requirements.txt`
   - `templates/index.html`
   - `static/css/style.css`
   - `static/js/app.js`

**Quick upload method:**
- Click "uploading an existing file"
- Drag all files/folders into the browser
- Click "Commit changes"

---

### Step 3: Deploy to Render

1. Go to https://render.com
2. Sign up (free - use your GitHub account)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo: `your-username/thinktank-os`
5. Fill in the form:
   - **Name**: `thinktank-os` (or whatever you want)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

6. **CRITICAL - Add Environment Variable:**
   - Click "Advanced"
   - Click "Add Environment Variable"
   - **Key**: `GROQ_API_KEY`
   - **Value**: Paste your Groq API key from Step 1

7. Click "Create Web Service"

---

### Step 4: Wait for Deploy (~2-3 minutes)

Render will:
- Clone your code
- Install dependencies
- Start your app

When you see "Your service is live 🎉", you're done!

Your URL will be: `https://thinktank-os.onrender.com`
(or whatever name you chose)

---

## ✅ Using Your Web App

1. Open your Render URL
2. Paste a consulting report URL **or** upload a PDF
3. Click "Add to Queue"
4. Click "Run All"
5. Wait ~5-10 seconds per report
6. Get 3 strategic opportunities!

---

## 🔒 Privacy & Security

- ✅ Reports are NOT stored (analyzed and deleted immediately)
- ✅ No user accounts (completely anonymous)
- ✅ Groq doesn't store your data
- ✅ SSL enabled automatically (https)

---

## 💰 Costs

**Free Tier Limits:**
- Groq: 14,400 requests/day (plenty for personal use)
- Render: 750 hours/month (always-on for small apps)

**If you exceed free tier:**
- Groq: Still free for most use
- Render: $7/month for always-on

**Realistic usage:**
- 100 reports/day = completely free
- 1000 reports/day = still mostly free

---

## 🛠️ Troubleshooting

### "Missing API Key" error
→ Make sure you added `GROQ_API_KEY` to environment variables in Render

### App sleeps after 15 min
→ Normal on free tier. First request wakes it up (~30 sec delay)

### Analysis fails
→ Check Groq API key is valid
→ Make sure the URL is a direct PDF link or accessible webpage

### Want to update the app
→ Push changes to GitHub
→ Render auto-deploys (takes 2 min)

---

## 📊 Monitoring

**Check your usage:**
- Groq: https://console.groq.com (shows API calls)
- Render: Dashboard shows requests, uptime, logs

---

## 🎨 Customization

### Change branding:
Edit `templates/index.html`:
- Line 7: Change title
- Line 12: Change header text

### Change colors:
Edit `static/css/style.css`:
- Line 10: Change gradient background

### Change AI model:
Edit `app.py`:
- Line 30: Change `GROQ_MODEL` to:
  - `mixtral-8x7b-32768` (faster, less smart)
  - `llama-3.1-70b-versatile` (balanced)
  - `llama3-groq-70b-8192-tool-use-preview` (best quality)

---

## 🚀 Next Steps (Optional)

### Add custom domain:
1. Buy a domain (Namecheap, Google Domains)
2. In Render, go to Settings → Custom Domain
3. Add your domain and follow DNS instructions

### Add analytics:
- Google Analytics
- Plausible (privacy-focused)

### Scale up:
- Render: Upgrade to $7/month for faster performance
- Groq: Always fast and generous free tier

---

## 📞 Support

**Issues with:**
- Deployment → Check Render logs
- API → Check Groq console
- Code bugs → Check browser console (F12)

**Need help?**
- Render docs: https://render.com/docs
- Groq docs: https://console.groq.com/docs

---

## 🎉 You're Live!

Your Think Tank OS is now accessible from anywhere in the world at:
`https://your-app-name.onrender.com`

Share it, use it, enjoy it! 🚀
