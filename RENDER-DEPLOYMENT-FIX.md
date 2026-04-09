# Render Deployment Fix - Step by Step

## **Current Issue:**
The deployment is using the root package.json instead of individual service configurations.

## **Solution: Create Individual Services Manually**

### **Step 1: Delete Current Failed Service**
1. Go to Render dashboard
2. Find the failed service
3. Click "Delete" to remove it

### **Step 2: Create Backend Service**
1. **Go to Render Dashboard**: https://render.com
2. **Click "New +"** then **"Web Service"**
3. **Connect Repository**: Select `Campus-Genie`
4. **Configure Service**:
   - **Name**: `campusgenie-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements-render.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   ```
   OLLAMA_MODEL=gemma:2b
   OLLAMA_BASE_URL=https://campusgenie-ollama.onrender.com
   CHROMA_HOST=campusgenie-chroma.onrender.com
   CHROMA_PORT=8000
   CHROMA_COLLECTION=campus_docs
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8080
   MAX_UPLOAD_SIZE_MB=50
   CHUNK_SIZE=500
   CHUNK_OVERLAP=50
   RETRIEVAL_TOP_K=5
   UPLOAD_DIR=/tmp/uploads
   LOG_LEVEL=INFO
   CORS_ORIGINS=*
   ```
6. **Click "Create Web Service"**

### **Step 3: Create ChromaDB Service**
1. **Click "New +"** then **"Web Service"**
2. **Connect Repository**: Select `Campus-Genie`
3. **Configure Service**:
   - **Name**: `campusgenie-chroma`
   - **Root Directory**: `chromadb`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `chroma run --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   ```
   IS_PERSISTENT=TRUE
   PERSIST_DIRECTORY=/chroma/chroma
   ```
5. **Click "Create Web Service"**

### **Step 4: Create Ollama Service**
1. **Click "New +"** then **"Web Service"**
2. **Connect Repository**: Select `Campus-Genie`
3. **Configure Service**:
   - **Name**: `campusgenie-ollama`
   - **Root Directory**: `ollama`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `ollama serve --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   ```
   OLLAMA_KEEP_ALIVE=24h
   ```
5. **Click "Create Web Service"**

### **Step 5: Create Frontend Service**
1. **Click "New +"** then **"Web Service"**
2. **Connect Repository**: Select `Campus-Genie`
3. **Configure Service**:
   - **Name**: `campusgenie-frontend`
   - **Root Directory**: `frontend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements-render.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. **Environment Variables**:
   ```
   BACKEND_URL=https://campusgenie-backend.onrender.com
   API_TIMEOUT=120
   ```
5. **Click "Create Web Service"**

### **Step 6: Wait for All Services to Deploy**
- Each service will take 2-5 minutes to build
- Monitor the build logs in Render dashboard
- All services should show "Live" status

### **Step 7: Test Your Application**
1. **Test Backend Health**:
   ```
   https://campusgenie-backend.onrender.com/api/health
   ```

2. **Test Frontend**:
   ```
   https://campusgenie-frontend.onrender.com
   ```

3. **Upload a PDF and ask a question**

## **Expected URLs After Deployment:**
- **Frontend**: https://campusgenie-frontend.onrender.com
- **Backend API**: https://campusgenie-backend.onrender.com
- **ChromaDB**: https://campusgenie-chroma.onrender.com
- **Ollama**: https://campusgenie-ollama.onrender.com

## **Troubleshooting:**

### **If Backend Fails:**
- Check backend requirements-render.txt
- Verify environment variables
- Check build logs

### **If Frontend Fails:**
- Check frontend requirements-render.txt
- Verify BACKEND_URL environment variable
- Check app.py exists

### **If ChromaDB Fails:**
- Check chromadb/requirements.txt
- Verify start command

### **If Ollama Fails:**
- Check ollama/requirements.txt
- Verify start command

## **Success!**
Once all services are deployed, your CampusGenie will be fully functional with:
- Educational chat with proper citations
- Document upload and processing
- Vector search and retrieval
- Conversational AI capabilities

**Your RAG-powered educational AI assistant will be live!**
