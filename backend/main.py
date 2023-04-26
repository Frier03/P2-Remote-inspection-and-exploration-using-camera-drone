from fastapi import FastAPI
from routes.relay_routes import relay_router
from routes.frontend_routes import frontend_router
from middleware import middleware
from mongodb_handler import MongoDB
from fastapi.middleware.cors import CORSMiddleware

mongo = MongoDB()
mongo.connect(mongodb_username="admin", mongodb_password="kmEuqHYeiWydyKpc")

app = FastAPI()
app.include_router(relay_router, prefix="/v1/api/relay")
app.include_router(frontend_router, prefix="/v1/api/frontend")

app.middleware("http")(middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)