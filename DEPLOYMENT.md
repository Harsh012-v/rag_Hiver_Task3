# Vercel Deployment Instructions

This guide will help you deploy the Hiver RAG system to Vercel.

---

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For connecting your repository
3. **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)

---

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Login to Vercel

```bash
vercel login
```

#### 3. Deploy from Project Directory

```bash
cd C:\Users\Hp\Downloads\HIVER_TASK3
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Select your account
- **Link to existing project?** No
- **Project name?** hiver-rag-system (or your choice)
- **Directory?** ./ (current directory)
- **Override settings?** No

#### 4. Add Environment Variables

After initial deployment, add your OpenAI API key:

```bash
vercel env add OPENAI_API_KEY
```

When prompted:
- **Value?** Paste your OpenAI API key
- **Environment?** Production, Preview, Development (select all)

#### 5. Redeploy with Environment Variables

```bash
vercel --prod
```

---

### Option 2: Deploy via Vercel Dashboard

#### 1. Push to GitHub

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit - Hiver RAG System"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/hiver-rag-system.git
git branch -M main
git push -u origin main
```

#### 2. Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Git Repository"
3. Select your GitHub repository
4. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)

#### 3. Add Environment Variables

In the Vercel dashboard:
1. Go to **Settings** → **Environment Variables**
2. Add variable:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key
   - **Environments**: Production, Preview, Development

#### 4. Deploy

Click **Deploy** and wait for the build to complete.

---

## Important Notes

### Backend Limitations on Vercel

⚠️ **Vercel Serverless Function Limits**:
- **Max execution time**: 10 seconds (Hobby), 60 seconds (Pro)
- **Max payload size**: 4.5 MB
- **Memory**: 1024 MB (Hobby), 3008 MB (Pro)

The first request may be slow (~5-10 seconds) as it loads the embedding model. Subsequent requests will be faster due to caching.

### Alternative: Separate Backend Deployment

For better performance, consider deploying the backend separately:

**Backend Options**:
- **Railway**: Excellent for Python apps, always-on containers
- **Render**: Free tier with persistent containers
- **Fly.io**: Global edge deployment
- **AWS Lambda**: With larger memory/timeout limits

**Frontend on Vercel**:
Keep the frontend on Vercel and update `app.js` to point to your backend URL:

```javascript
const API_BASE_URL = 'https://your-backend-url.railway.app';
```

---

## Recommended Deployment Strategy

### Best Approach: Split Deployment

1. **Backend on Railway** (or similar):
   - Always-on container
   - No cold starts
   - Better for ML models
   - Cost: ~$5/month

2. **Frontend on Vercel**:
   - Free tier
   - Global CDN
   - Automatic HTTPS

### Railway Deployment (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variable
railway variables set OPENAI_API_KEY=your_key_here
```

Update `frontend/app.js`:
```javascript
const API_BASE_URL = 'https://your-app.railway.app';
```

Then deploy frontend to Vercel as usual.

---

## Vercel Configuration Files

The following files have been added/updated for Vercel deployment:

### `vercel.json`
Configures how Vercel builds and routes your application.

### `backend/main.py`
Updated with:
- `/api` prefix for all routes
- Singleton pattern for RAG engine (serverless optimization)
- CORS configuration for Vercel domains

### `frontend/app.js`
Updated with:
- Dynamic API URL detection (local vs. production)
- Automatic switching between localhost and Vercel

---

## Testing Your Deployment

### 1. Check Health Endpoint

```bash
curl https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "rag_engine_initialized": true,
  "openai_configured": true
}
```

### 2. Test Query Endpoint

```bash
curl -X POST https://your-app.vercel.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure automations in Hiver?", "k": 3}'
```

### 3. Open Frontend

Visit: `https://your-app.vercel.app`

---

## Troubleshooting

### Issue: "RAG engine not initialized"

**Cause**: Model loading timeout or memory limit

**Solutions**:
1. Upgrade to Vercel Pro (60s timeout)
2. Use a smaller embedding model
3. Deploy backend separately (recommended)

### Issue: "Module not found"

**Cause**: Missing dependencies in `requirements.txt`

**Solution**:
```bash
# Ensure all dependencies are listed
pip freeze > backend/requirements.txt
vercel --prod
```

### Issue: Slow first request

**Cause**: Cold start loading embedding model

**Solutions**:
1. This is normal for serverless
2. Consider Railway/Render for always-on backend
3. Implement model caching (already done in code)

### Issue: CORS errors

**Cause**: Frontend domain not allowed

**Solution**: Update `backend/main.py`:
```python
allow_origins=["https://your-app.vercel.app"]
```

---

## Performance Optimization

### 1. Enable Caching

Vercel automatically caches static assets. For API responses:

```python
# In main.py, add cache headers
from fastapi.responses import JSONResponse

@app.get("/api/stats")
async def get_stats():
    # ... existing code ...
    return JSONResponse(
        content=stats,
        headers={"Cache-Control": "public, max-age=3600"}
    )
```

### 2. Use Edge Functions (Pro)

For even faster response times, consider Vercel Edge Functions.

### 3. Optimize Model Loading

Consider using a lighter model for faster cold starts:
```python
# In rag_engine.py
model = EmbeddingModel("all-MiniLM-L6-v2")  # Current: 384 dim
# or
model = EmbeddingModel("paraphrase-MiniLM-L3-v2")  # Lighter: 384 dim, faster
```

---

## Cost Estimation

### Vercel (Frontend + Backend)
- **Hobby Plan**: Free
  - 100 GB bandwidth
  - 100 GB-hours serverless execution
  - 10s function timeout
  - **Limitation**: May timeout on first request

- **Pro Plan**: $20/month
  - 1 TB bandwidth
  - 1000 GB-hours execution
  - 60s function timeout
  - **Better for**: ML workloads

### Railway (Backend Only)
- **Free Trial**: $5 credit
- **Hobby Plan**: ~$5-10/month
  - Always-on container
  - No cold starts
  - 8 GB RAM
  - **Recommended for**: This project

### Total Recommended Cost
- **Frontend (Vercel)**: Free
- **Backend (Railway)**: $5-10/month
- **OpenAI API**: Pay-per-use (~$0.002 per query)

---

## Next Steps

1. **Deploy to Vercel** using Option 1 or 2 above
2. **Test the deployment** with both required queries
3. **Monitor performance** in Vercel dashboard
4. **Consider Railway** if you experience timeouts

---

## Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **FastAPI on Vercel**: [vercel.com/guides/python](https://vercel.com/guides/python)

---

**Ready to deploy!** 🚀
