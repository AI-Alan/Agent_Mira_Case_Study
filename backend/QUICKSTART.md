# Quick Start Guide

## Problem: "Attribute 'app' not found in module 'main'"

This error occurs because **FastAPI is not installed**. Follow these steps:

## Solution

### Step 1: Create Virtual Environment
```bash
cd backend
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install fastapi uvicorn pydantic python-dotenv
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import fastapi; print('FastAPI installed successfully')"
```

### Step 5: Start Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Test Setup

Run the test script to verify everything works:
```bash
python test_setup.py
```

## API Endpoints

Once running, the API will be available at:
- **Server**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Chat**: POST http://127.0.0.1:8000/chat/message
- **Properties**: GET http://127.0.0.1:8000/properties

## Frontend Connection

The frontend is configured to connect to `http://127.0.0.1:8000`. Make sure:
1. Backend is running on port 8000
2. Frontend has `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` in `.env.local`

## Troubleshooting

### Still getting "app not found" error?
1. Make sure virtual environment is activated: `source venv/bin/activate`
2. Verify FastAPI is installed: `pip list | grep fastapi`
3. Check if you're in the correct directory: `pwd` should show `.../backend`
4. Try running test script: `python test_setup.py`

### Port 8000 already in use?
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

