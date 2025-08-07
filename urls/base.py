from fastapi import APIRouter
from api.authView import auth_router

router = APIRouter()

router.include_router(auth_router, tags= ['Auth'])