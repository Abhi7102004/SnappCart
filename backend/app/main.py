from fastapi import FastAPI

app= FastAPI(
    title="SnappCart API",
    version="0.1.0",
    description="Backend for SnappCart e-commerce platform"
)

@app.get("/")
def root():
    return {"message": "SnappCart API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "snappcart-backend"}
