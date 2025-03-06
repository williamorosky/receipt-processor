FROM python:3.9-slim

WORKDIR /app

# Copy the entire repository into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "receipt_processor.main:app", "--host", "0.0.0.0", "--port", "8000"]
