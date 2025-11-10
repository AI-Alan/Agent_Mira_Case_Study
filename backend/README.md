# Agent Mira Backend

FastAPI backend for the Agent Mira real estate chatbot.

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start the server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or use the provided script:
```bash
./start.sh
```

## API Endpoints

- **Base URL**: `http://127.0.0.1:8000`
- **API Docs**: `http://127.0.0.1:8000/docs`
- **Chat Message**: `POST /chat/message`
- **Properties**: `GET /properties?location=...&budget=...&bedrooms=...`
- **Save Property**: `POST /user/save`

## Data Structure

The backend merges data from three JSON files:
- `data/property_basics.json` - Basic property info (id, title, price, location)
- `data/property_characteristics.json` - Property details (bedrooms, bathrooms, amenities)
- `data/property_images.json` - Property images

## Features

- ✅ Merges data from multiple JSON files
- ✅ Filters properties by location, budget, and bedrooms
- ✅ Supports both Indian (INR) and US (USD) properties
- ✅ NLP-based filter extraction from chat messages
- ✅ Random response messages for better UX
- ✅ CORS enabled for frontend integration

## Troubleshooting

### Error: "Attribute 'app' not found in module 'main'"

This error occurs when FastAPI is not installed. Solution:
1. Make sure virtual environment is activated: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Verify installation: `python -c "import fastapi; print('OK')"`

### Error: "No module named 'fastapi'"

Install FastAPI in the virtual environment:
```bash
source venv/bin/activate
pip install fastapi uvicorn pydantic python-dotenv
```

## Environment Variables

Create a `.env` file (optional):
```
API_HOST=127.0.0.1
API_PORT=8000
```

