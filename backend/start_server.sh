#!/bin/bash

# Start Backend Server Script

cd "$(dirname "$0")"

echo "🚀 Starting Agent Mira Backend Server..."
echo ""

# Check for virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating venv..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activating .venv..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found!"
    echo "Please create one: python3 -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env template..."
    cat > .env << EOF
MONGO_URI=mongodb+srv://aman:aman1234@cluster0.riddt7x.mongodb.net/?appName=cluster0&retryWrites=true&w=majority
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_NAME=agent_mira
EOF
    echo "✅ Created .env file. Please update it with your credentials."
    echo ""
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "✅ Starting server on http://127.0.0.1:8000"
echo "📚 API Docs will be available at http://127.0.0.1:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the server
uvicorn main:app --reload --host 127.0.0.1 --port 8000

