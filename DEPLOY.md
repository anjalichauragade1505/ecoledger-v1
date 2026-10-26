# EcoLedger - Deploy (3 steps)
1. MongoDB Atlas (free): create cluster -> Database Access: add user+password -> Network Access: allow 0.0.0.0/0 -> Connect -> Drivers -> copy connection string, put your password in it.
2. Render (Root Dir: backend): Build `pip install -r requirements.txt`, Start `uvicorn main:app --host 0.0.0.0 --port $PORT`
   Env: PYTHON_VERSION=3.11.9, ADMIN_EMAIL, ADMIN_PASSWORD, JWT_SECRET, MONGODB_URI, CORS_ORIGINS=*
3. Vercel (Root Dir: frontend): Env: REACT_APP_API_URL=<render url, no trailing />, CI=false
