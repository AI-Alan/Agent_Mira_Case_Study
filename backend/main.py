from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routes import chat_routes, property_routes, user_routes, auth_routes
from fastapi.middleware.cors import CORSMiddleware
from core.db import test_connection

app = FastAPI(title="Agent Mira Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(property_routes.router, prefix="/properties", tags=["Properties"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])

@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""
    result = await test_connection()
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"📦 Database: {result['database']}")
    else:
        print(f"⚠️  {result['message']}")
        print(f"💡 Hint: {result.get('hint', '')}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide better error messages"""
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors(),
            "message": "Validation error. Please check your input."
        }
    )

@app.get("/")
def root():
    return {"message": "Agent Mira API is running 🚀"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = await test_connection()
    return {
        "status": "ok",
        "database": db_status
    }