# Receipt Processor

## How to Run
#### 1. Build the Docker Container
```bash
docker build -t receipt-processor .
```
#### 2. Run it
```bash
docker run -d -p 8000:8000 receipt-processor
```
#### 3. Check out the API docs
```bash
open http://localhost:8000/docs
```
#### 4. Get some curls in 💪
Using the provided example `simple-receipt.json`
```bash
curl --location 'http://127.0.0.1:8000/receipts/process' \
--header 'Content-Type: application/json' \
--data '{
    "retailer": "Target",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "13:13",
    "total": "1.25",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"}
    ]
}'
```
Using the provided example `morning-receipt.json`
```bash
curl --location 'http://127.0.0.1:8000/receipts/process' \
--header 'Content-Type: application/json' \
--data '{
    "retailer": "Walgreens",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "08:13",
    "total": "2.65",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
        {"shortDescription": "Dasani", "price": "1.40"}
    ]
}'
```