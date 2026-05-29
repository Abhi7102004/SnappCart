# Step 1 — Base image
FROM python:3.13-slim

# Step 2 — Set working directory inside container
# All commands after this run from /app
# Think of it as cd /app inside the container
WORKDIR /app

# Step 3 — Copy requirements first (before code)
# WHY: Docker caches layers
# If we copy code first, ANY code change = reinstall all packages
# This way packages only reinstall when requirements.txt changes
COPY requirements.txt .

# Step 4 — Install Python packages
# --no-cache-dir = don't store install cache (keeps image small)
RUN pip install --no-cache-dir -r requirements.txt

# Step 5 — Copy rest of the code
# . (source) = everything in backend/
# . (dest)   = /app inside container
COPY . .

# Step 6 — Expose port so outside world can reach the app
EXPOSE 8000

# Step 7 — Command to run when container starts
# uvicorn = ASGI server that runs FastAPI
# app.main:app = file app/main.py, variable named app
# --host 0.0.0.0 = accept connections from outside container
# --reload = auto restart on code change (dev only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]