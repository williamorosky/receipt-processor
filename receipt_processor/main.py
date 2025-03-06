import uuid
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from receipt_processor.models import Receipt, ProcessResponse, PointsResponse
from receipt_processor.services import calculate_points
from receipt_processor.store import receipt_store

logger = logging.getLogger("receipt_processor")
logging.basicConfig(level=logging.INFO)

app = FastAPI()


# Custom handler for Pydantic validation errors.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log detailed validation error info.
    logger.error(
        f"Validation error at {request.url}. Errors: {exc.errors()}. Request body: {exc.body}"
    )
    # Return a 400 Bad Request following the API spec.
    return JSONResponse(
        status_code=400,
        content={"detail": "The receipt is invalid."},
    )


# Generic exception handler that adjusts response based on endpoint.
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception at {request.url}: {exc}")
    # If the error occurred during receipt processing, return 400 as specified.
    if request.url.path.startswith("/receipts/process"):
        return JSONResponse(
            status_code=400,
            content={"detail": "The receipt is invalid."},
        )
    # Otherwise, for other endpoints, return a generic 500 error.
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error."
        },
    )


@app.post("/receipts/process", response_model=ProcessResponse)
def process_receipt(receipt: Receipt):
    # Pydantic automatically validates the request before reaching this point.
    points = calculate_points(receipt)
    receipt_id = str(uuid.uuid4())
    receipt_store.save(receipt_id, points)
    logger.info(f"Processed receipt {receipt_id} with {points} points.")
    return ProcessResponse(id=receipt_id)


@app.get("/receipts/{receipt_id}/points", response_model=PointsResponse)
def get_points(receipt_id: str):
    points = receipt_store.get(receipt_id)
    if points is None:
        logger.warning(f"Receipt ID {receipt_id} not found.")
        # Return error message as specified in the API.
        raise HTTPException(status_code=404, detail="No receipt found for that ID.")
    logger.info(f"Retrieved points for receipt {receipt_id}: {points}")
    return PointsResponse(points=points)
