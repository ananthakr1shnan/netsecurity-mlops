FROM python:3.10-slim-buster

WORKDIR /app

COPY . .

RUN apt update && apt install -y awscli

# Create necessary directories
RUN mkdir -p prediction_output final_model templates

RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

EXPOSE 8000

# Use Render's dynamic PORT environment variable
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
