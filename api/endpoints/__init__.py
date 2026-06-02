from fastapi import APIRouter
from .products import router as catalog_router
from .client import router as client_router
from .order import router as order_router
from .seller import router as seller_router
from .auth import router as auth_router
from .admin import router as admin_router

main_router = APIRouter(prefix="/api")
main_router.include_router(catalog_router)
main_router.include_router(client_router)
main_router.include_router(order_router)
main_router.include_router(seller_router)
main_router.include_router(auth_router)
main_router.include_router(admin_router)