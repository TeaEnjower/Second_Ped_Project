from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.handlers import user_router, category_router, article_router  
from api.login_handler import login_router
from middleware import auth_middleware  

app = FastAPI(title="Marketplace Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(auth_middleware)

main_api_router = APIRouter()

main_api_router.include_router(login_router, prefix='/auth', tags=['auth'])
main_api_router.include_router(user_router, prefix='/user', tags=['user'])
main_api_router.include_router(category_router, prefix='/category', tags=['category'])
main_api_router.include_router(article_router, prefix='/article', tags=['article'])

app.include_router(main_api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)