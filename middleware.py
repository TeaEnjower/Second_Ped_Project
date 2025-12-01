# middleware.py
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from settings import SECRET_KEY, ALGORITHM

async def auth_middleware(request: Request, call_next):
   
    public_routes = [
        "/auth/login",
        "/auth/login-form", 
        "/user/",
        "/category/",
        "/article/",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    

    if request.url.path in public_routes or request.url.path.startswith("/docs"):
        return await call_next(request)
    
    token = request.cookies.get("access_token")
    
    if not token and "authorization" in request.headers:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user = payload 
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await call_next(request)