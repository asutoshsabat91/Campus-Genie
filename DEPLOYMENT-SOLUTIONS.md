# CampusGenie Deployment Solutions

## 🚨 Current Issue: Lambda Size Limits

Vercel's free tier has a **500MB limit** for Lambda functions. Our current dependencies exceed this limit.

## 💡 Solutions

### Option 1: Use External Services (Recommended)

**Deploy backend API only to Vercel, use external ChromaDB and Ollama:**

1. **Deploy Backend to Vercel:**
   ```bash
   cd "/Users/asutoshsabat/Campus Genie Final"
   cp vercel-backend.json vercel.json
   vercel --prod --yes
   ```

2. **Set up External ChromaDB:**
   - Use ChromaDB Cloud (free tier) or self-hosted
   - Update environment: `CHROMA_HOST=https://your-chroma-url`

3. **Set up External Ollama:**
   - Use Ollama Cloud or self-hosted service
   - Update environment: `OLLAMA_BASE_URL=https://your-ollama-url`

4. **Deploy Frontend Separately:**
   - Deploy Streamlit to Vercel or Netlify
   - Update `BACKEND_URL` to point to deployed API

### Option 2: Optimize Dependencies

**Reduce package size by removing unused dependencies:**

1. **Create ultra-minimal backend:**
   ```python
   # Only essential FastAPI dependencies
   from fastapi import FastAPI
   import httpx
   
   # Remove langchain, chromadb client (use external)
   # Only keep ollama client
   ```

2. **Use smaller alternatives:**
   - Replace `sentence-transformers` with smaller embedding models
   - Use `ollama-python` instead of `langchain-ollama`

### Option 3: Upgrade Vercel Plan

**Move to Vercel Pro plan for higher limits:**
- 100MB function size limit
- Better performance
- More deployment options

---

## 🔧 Quick Fix: External Services Setup

**For immediate deployment, use external ChromaDB + Ollama:**

```bash
# Deploy backend API only
cd "/Users/asutoshsabat/Campus Genie Final"
cp vercel-backend.json vercel.json
vercel --prod --yes

# Your API will be available at:
# https://campusgenie-api.vercel.app
```

**External Services to Set Up:**
- ChromaDB: https://docs.trychroma.com/deployment
- Ollama: https://docs.trychroma.com/deployment/ollama

**Frontend Deployment:**
Deploy Streamlit app separately to Vercel or Netlify, pointing to your API.

---

## 📊 Size Analysis

Current dependencies: **~4.9GB** (too large)
Minimal backend only: **~200MB** (within limits)
Optimized with external services: **~100MB** (well within limits)

**Recommendation**: Use external services for production deployment.
