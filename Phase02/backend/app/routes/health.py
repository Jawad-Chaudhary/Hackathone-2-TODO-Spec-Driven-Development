# [Task T074] Health check endpoint for monitoring and deployment verification

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment verification.

    Returns:
        dict: Status indicating the service is healthy

    Response:
        - status_code: 200
        - body: {"status": "healthy"}

    Notes:
        - No authentication required (public endpoint)
        - Used by load balancers, monitoring systems, and deployment pipelines
    """
    return {"status": "healthy"}
