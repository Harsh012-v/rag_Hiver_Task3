# Hiver RAG System - Quick Deploy to Vercel

## 🚀 One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/hiver-rag-system)

---

## ⚡ Quick Start (5 minutes)

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login

```bash
vercel login
```

### 3. Deploy

```bash
cd C:\Users\Hp\Downloads\HIVER_TASK3
vercel
```

### 4. Add OpenAI API Key

```bash
vercel env add OPENAI_API_KEY
```

Paste your OpenAI API key when prompted.

### 5. Redeploy

```bash
vercel --prod
```

**Done!** Your app is live at `https://your-app.vercel.app`

---

## ⚠️ Important: Vercel Limitations

Vercel serverless functions have a **10-second timeout** on the free plan. The first request may timeout while loading the embedding model.

### Recommended Solution: Split Deployment

**Backend → Railway (Always-On)**
**Frontend → Vercel (Free)**

This gives you:
- ✅ No timeouts
- ✅ Faster responses
- ✅ Better performance
- ✅ Only ~$5/month

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 📋 Checklist Before Deploy

- [ ] OpenAI API key ready
- [ ] Git repository initialized
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] All dependencies in `requirements.txt`

---

## 🔧 Files Modified for Vercel

1. **`vercel.json`** - Vercel configuration
2. **`backend/main.py`** - Added `/api` prefix, serverless optimization
3. **`frontend/app.js`** - Dynamic API URL detection
4. **`index.html`** - Root file for Vercel routing
5. **`.gitignore`** - Ignore sensitive files

---

## 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Detailed deployment options
- Railway setup guide
- Troubleshooting
- Performance optimization
- Cost analysis

---

## 🆘 Quick Troubleshooting

**Timeout on first request?**
→ Use Railway for backend (see DEPLOYMENT.md)

**CORS errors?**
→ Already configured in `backend/main.py`

**Module not found?**
→ Check `backend/requirements.txt`

---

**Ready to deploy!** 🎉
