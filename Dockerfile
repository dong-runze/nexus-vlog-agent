# Stage 1: Build & Install Dependencies
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime Image
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Ensure path includes the local bin
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Ensure data uploads directory exists inside container
RUN mkdir -p data/uploads

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Run FastAPI using uvicorn on port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
