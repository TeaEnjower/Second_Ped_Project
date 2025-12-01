from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from api.handlers import user_router, category_router, article_router

app = FastAPI(title="Marketplace")

main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(category_router, prefix="/category", tags=["category"])
main_api_router.include_router(article_router, prefix="/article", tags=["article"])

app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
