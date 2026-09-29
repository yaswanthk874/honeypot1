FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose API port and simulated service ports
EXPOSE 8000 8080 2222 33060

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
