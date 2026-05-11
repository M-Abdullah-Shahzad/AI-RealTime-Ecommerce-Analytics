# Multi-stage Dockerfile for BDA Analytics Platform
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    openjdk-11-jdk-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create data and output directories
RUN mkdir -p data outputs logs

# Expose ports
EXPOSE 8501 9092 7077 8080

# Default command - run all modules then dashboard
CMD ["bash", "-c", "python batch_processing.py && python visualization.py && python rfm_analysis.py && python churn_model.py && python ai_insights.py && python recommendation.py && streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0"]
