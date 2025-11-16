FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server files (including app.py which is now in server/)
COPY server/ .

# Copy pre-built frontend
COPY frontend/dist/ ./frontend/dist/

EXPOSE 5000

# app.py is now in the current directory (copied from server/)
CMD ["python", "app.py"]