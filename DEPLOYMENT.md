# CampusGenie Deployment Guide

This guide provides comprehensive deployment instructions for CampusGenie on modern cloud platforms.

## 🚀 Supported Platforms

### 1. Vercel (Recommended)
**Best for**: Serverless deployment with automatic scaling
**Pros**: Free tier, excellent performance, global CDN
**Cons**: Limited build times, cold starts

### 2. Render (Alternative)
**Best for**: Persistent services with custom domains
**Pros**: Free tier available, persistent storage
**Cons**: Longer deployment times, manual scaling

---

## 📋 Vercel Deployment

### Prerequisites
- Vercel account
- GitHub repository
- Vercel CLI installed

### Step-by-Step Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Root**
   ```bash
   cd /path/to/Campus-Genie-Final
   vercel --prod
   ```

4. **Environment Variables**
   Set these in Vercel dashboard:
   ```
   OLLAMA_MODEL=gemma:2b
   OLLAMA_BASE_URL=https://your-ollama-url.vercel.app
   CHROMA_HOST=https://your-chroma-url.vercel.app
   CHROMA_PORT=8000
   ```

### Vercel Configuration
- `vercel.json`: Defines build and routing rules
- `vercel-ollama/ollama.js`: Ollama proxy function
- `package.json`: Dependencies and metadata

---

## 🎯 Render Deployment

### Prerequisites
- Render account
- GitHub repository
- Render CLI installed

### Step-by-Step Deployment

1. **Connect GitHub to Render**
   - Go to Render dashboard
   - Connect your repository
   - Select "Web Service"

2. **Create Services**
   Create 4 services:
   - `backend` (Python, FastAPI)
   - `chromadb` (Python, ChromaDB)
   - `ollama` (Python, Ollama)
   - `frontend` (Python, Streamlit)

3. **Configure Environment Variables**
   Set these for each service:
   ```
   OLLAMA_MODEL=gemma:2b
   OLLAMA_BASE_URL=http://ollama-service-url.onrender.com
   CHROMA_HOST=chromadb-service-url.onrender.com
   ```

4. **Deploy**
   - Push to GitHub
   - Render auto-deploys

### Render Configuration
- `render.yaml`: Complete service definitions
- `docker-compose.prod.yml`: Production Docker setup

---

## 🔧 Production Considerations

### Security
- Use HTTPS endpoints
- Set proper CORS origins
- Implement rate limiting
- Secure file uploads

### Performance
- Optimize for cold starts
- Use CDN for static assets
- Implement caching strategies

### Monitoring
- Set up health checks
- Monitor resource usage
- Log application metrics

---

## 🌐 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend    │    │   Backend     │    │   ChromaDB   │
│  (Streamlit)  │────│  (FastAPI)    │────│ (Vector DB)   │
│   :8501        │    │   :8080        │    │   :8000        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                      │
         │                      │                      │
         └──────────────────┬──────────────────┘
                                │
                       ┌─────────────────┐
                       │   Ollama      │
                       │  (Gemma 2B)   │
                       │   :11434        │
                       └─────────────────┘
```

---

## 📱 Access URLs

After deployment:
- **Frontend**: `https://your-app.vercel.app` or `https://your-app.onrender.com`
- **Backend API**: `https://your-app.vercel.app/api` or `https://your-backend.onrender.com`
- **Health Check**: `https://your-app.vercel.app/api/health`

---

## 🛠 Troubleshooting

### Common Issues
1. **Cold Starts**: First request may be slow
2. **Memory Limits**: Monitor resource usage
3. **CORS Issues**: Check environment variables
4. **Database Connection**: Verify service URLs

### Solutions
- Implement warm-up strategies
- Use appropriate instance sizes
- Test endpoints individually
- Monitor logs regularly

---

## 📞 Support

For deployment issues:
- Check Vercel/Render logs
- Review this guide
- Open GitHub issue
- Contact deployment platform support
