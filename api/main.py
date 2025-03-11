from fastapi import FastAPI
from .routes import router


app = FastAPI()

app.include_router(router)  # Include the routes

# Root endpoint (optional)
@app.get("/")
async def home():
    return {"message": "Welcome to the Invoice Processing API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="localhost", port=8000)