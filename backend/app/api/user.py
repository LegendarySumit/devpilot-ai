from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def user_status() -> dict[str, str]:
    return {"module": "user", "status": "ready"}
