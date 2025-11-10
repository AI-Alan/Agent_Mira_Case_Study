from fastapi import FastAPI
from routes import chat_routes, property_routes, user_routes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Agent Mira Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(property_routes.router, prefix="/properties", tags=["Properties"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])

@app.get("/")
def root():
    return {"message": "Agent Mira API is running 🚀"}