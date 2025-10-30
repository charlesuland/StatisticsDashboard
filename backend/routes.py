from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return

@router.get("/login")
def loginPage():
    return

@router.post("/login")
def authenticate():
    return