# 🚀 Vercel Deployment Guide (Updated for TF-IDF Backend)

## ✅ Your Project is Ready for Vercel!

The system now uses a lightweight TF-IDF backend that works perfectly on Vercel.

---

## 📋 Pre-Deployment Checklist

- [x] Lightweight backend (`main_tfidf.py`)
- [x] Updated `vercel.json`
- [x] Updated `requirements.txt` (no heavy dependencies)
- [x] Frontend configured
- [x] KB articles ready
- [ ] Git repository initialized
- [ ] Vercel CLI installed

---

## 🚀 Quick Deploy (5 Minutes)

### Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

### Step 2: Login to Vercel

```powershell
vercel login
```

### Step 3: Initialize Git (if not done)

```powershell
cd C:\Users\Hp\Downloads\HIVER_TASK3
git init
git add .
git commit -m "Initial commit - Hiver RAG System with TF-IDF"
```

### Step 4: Deploy

```powershell
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** hiver-rag-system
- **Directory?** ./
- **Override settings?** No

### Step 5: Deploy to Production

```powershell
vercel --prod
```

---

## ⚡ Performance on Vercel

### Expected Performance:
- **Cold Start:** ~2-3 seconds (first request)
- **Warm Requests:** ~200-500ms
- **Timeout Risk:** ✅ Low (TF-IDF loads quickly)

### Why It Works Now:
- ❌ **Before:** sentence-transformers (90MB model, 10+ seconds to load)
- ✅ **Now:** scikit-learn TF-IDF (lightweight, <1 second to load)

---

## 🔧 What Changed for Vercel

### 1. Backend File
- **Old:** `backend/main.py` (sentence-transformers)
- **New:** `backend/main_tfidf.py` (TF-IDF)

### 2. Dependencies
- **Removed:** `sentence-transformers`, `faiss-cpu`, `openai`
- **Added:** `scikit-learn` (much lighter)

### 3. Configuration
- **Updated:** `vercel.json` to use `main_tfidf.py`
- **Updated:** `requirements.txt` with lighter dependencies

---

## 📊 Vercel Deployment Options

### Option 1: Vercel (Recommended for This Project)

**Pros:**
- ✅ Works perfectly with TF-IDF backend
- ✅ Free tier sufficient
- ✅ Fast deployment
- ✅ No timeout issues

**Cost:** FREE

**Deploy:**
```bash
vercel --prod
```

---

### Option 2: Railway (If You Want Always-On)

**Pros:**
- ✅ Always-on container
- ✅ No cold starts
- ✅ Better for high traffic

**Cost:** ~$5/month

**Deploy:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## 🧪 Test After Deployment

### 1. Check Health

```bash
curl https://your-app.vercel.app/api/health
```

Expected:
```json
{
  "status": "healthy",
  "rag_engine_initialized": true,
  "articles_loaded": 8
}
```

### 2. Test Query

```bash
curl -X POST https://your-app.vercel.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure automations in Hiver?", "k": 3}'
```

### 3. Open Frontend

Visit: `https://your-app.vercel.app`

---

## 📁 Project Structure for Deployment

```
HIVER_TASK3/
├── vercel.json              ← Updated for main_tfidf.py
├── index.html               ← Root HTML
├── package.json
├── .gitignore
│
├── backend/
│   ├── main_tfidf.py        ← NEW: Lightweight backend
│   ├── requirements.txt     ← Updated dependencies
│   └── .env.example
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js               ← Uses /api/query
│
└── kb_articles/             ← 8 articles
```

---

## ⚠️ Important Notes

### 1. No OpenAI API Key Needed
The TF-IDF version doesn't use OpenAI, so you don't need an API key!

### 2. Vercel Limits (Free Tier)
- ✅ Bandwidth: 100 GB/month (plenty)
- ✅ Execution: 100 GB-hours (plenty)
- ✅ Timeout: 10 seconds (TF-IDF loads in <1s)

### 3. Git Required
Vercel needs a git repository. Make sure to:
```bash
git init
git add .
git commit -m "Initial commit"
```

---

## 🎯 Deployment Commands Summary

```powershell
# 1. Initialize Git
git init
git add .
git commit -m "Hiver RAG System"

# 2. Deploy to Vercel
vercel

# 3. Deploy to Production
vercel --prod

# Done! Your app is live at: https://your-app.vercel.app
```

---

## ✅ Success Checklist

After deployment:
- [ ] Health endpoint returns healthy
- [ ] Query endpoint works
- [ ] Frontend loads
- [ ] Both test queries work:
  - "How do I configure automations in Hiver?"
  - "Why is CSAT not appearing?"
- [ ] Results show in <1 second

---

## 🆘 Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure `requirements.txt` is updated
```bash
cd backend
cat requirements.txt  # Should show scikit-learn, not sentence-transformers
```

### Issue: Deployment fails
**Solution:** Check Vercel logs
```bash
vercel logs
```

### Issue: Timeout
**Solution:** This shouldn't happen with TF-IDF, but if it does:
- Check Vercel function logs
- Ensure `main_tfidf.py` is being used

---

## 🎉 You're Ready!

Your project is now optimized for Vercel deployment with:
- ✅ Lightweight TF-IDF backend
- ✅ Fast loading (<1 second)
- ✅ No heavy dependencies
- ✅ Works on free tier
- ✅ Production-ready

**Just run:** `vercel --prod` 🚀
