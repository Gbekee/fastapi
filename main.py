# from alembic import env
from urls.base import router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from settings import DOMAIN_URL
from models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # You could connect to the database or load other resources here if needed
   yield
    # Optional cleanup

# Create the FastAPI app instance
app = FastAPI(lifespan=lifespan)




# Define allowed origins (e.g., front-end URL)
origins = [
    "http://localhost:3000",     # for local React/Vue dev server
    DOMAIN_URL
    # "https://your-frontend.com", # for production frontend
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] to allow all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],              # allow all HTTP methods
    allow_headers=["*"],              # allow all headers
)
# Include your routers
app.include_router(router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
