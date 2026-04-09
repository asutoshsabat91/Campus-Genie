# CampusGenie Auto-Deploy Guide

## **One-Click Deployment to Render**

### **Option 1: Web-Based Auto-Deploy (Easiest)**

**Step 1: Go to Render Dashboard**
1. Visit: https://render.com
2. Sign up/login with GitHub
3. Click "New +" -> "Web Service"

**Step 2: Connect Repository**
1. Select your `Campus-Genie` repository
2. Choose branch: `main`
3. Click "Connect"

**Step 3: Auto-Configure Services**
1. **Backend Service:**
   - Name: `campusgenie-backend`
   - Root Directory: `backend`
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **ChromaDB Service:**
   - Name: `campusgenie-chroma`
   - Root Directory: `backend`
   - Runtime: `Python`
   - Build Command: `pip install chromadb==0.5.3`
   - Start Command: `chroma run --host 0.0.0.0 --port $PORT`

3. **Ollama Service:**
   - Name: `campusgenie-ollama`
   - Root Directory: `backend`
   - Runtime: `Python`
   - Build Command: `pip install ollama`
   - Start Command: `ollama serve --host 0.0.0.0 --port $PORT`

4. **Frontend Service:**
   - Name: `campusgenie-frontend`
   - Root Directory: `frontend`
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

**Step 4: Set Environment Variables**
```
# Backend Service
OLLAMA_MODEL=gemma:2b
OLLAMA_BASE_URL=https://campusgenie-ollama.onrender.com
CHROMA_HOST=campusgenie-chroma.onrender.com
CHROMA_PORT=8000
CHROMA_COLLECTION=campus_docs

# Frontend Service
BACKEND_URL=https://campusgenie-backend.onrender.com
API_TIMEOUT=120
```

**Step 5: Deploy**
- Click "Create Web Service" for each service
- Wait for deployment to complete
- Test the application

### **Option 2: CLI Auto-Deploy (Advanced)**

**Install Render CLI:**
```bash
npm install -g @render/cli
render login
```

**Run Auto-Deploy Script:**
```bash
cd "/Users/asutoshsabat/Campus Genie Final"
./render-auto-deploy.sh
```

### **Option 3: Docker Auto-Deploy (Local)**

**Deploy with Docker Compose:**
```bash
cd "/Users/asutoshsabat/Campus Genie Final"
docker-compose -f docker-compose.prod.yml up -d
```

## **Deployment URLs**

After deployment, your CampusGenie will be available at:
- **Frontend**: https://campusgenie-frontend.onrender.com
- **Backend API**: https://campusgenie-backend.onrender.com
- **Health Check**: https://campusgenie-backend.onrender.com/api/health

## **Testing Your Deployment**

1. **Test Backend Health:**
   ```bash
   curl https://campusgenie-backend.onrender.com/api/health
   ```

2. **Test Frontend:**
   - Visit: https://campusgenie-frontend.onrender.com
   - Upload a PDF document
   - Ask a question

3. **Test API:**
   ```bash
   curl -X POST https://campusgenie-backend.onrender.com/api/chat/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this document about?"}'
   ```

## **Troubleshooting**

### **Common Issues:**
1. **Build Failures**: Check logs for missing dependencies
2. **Service Not Starting**: Verify start commands
3. **Connection Errors**: Check environment variables
4. **Timeout Issues**: Increase timeout values

### **Solutions:**
1. **Review Build Logs**: Check Render dashboard logs
2. **Verify Environment Variables**: Ensure all variables are set
3. **Test Services Individually**: Deploy one service at a time
4. **Check Network Configuration**: Verify service URLs

## **Support**

For deployment issues:
- Check Render dashboard logs
- Review environment variables
- Test services individually
- Contact Render support

## **Success!**

Once deployed, your CampusGenie will be:
- **Live on the internet** with custom URLs
- **Fully functional** with RAG capabilities
- **Scalable** with Render's infrastructure
- **Professional** with custom domains (optional)

**Your RAG-powered educational AI assistant is ready to serve students worldwide!**
