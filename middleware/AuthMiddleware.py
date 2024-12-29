from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
from starlette.responses import JSONResponse
import json
from redis_client import redis_client


class AuthMiddleware(BaseHTTPMiddleware):
    """
    User should be logged-in to perform CRUD on form, and also to submit another form
    """
    
    async def dispatch(self, request, call_next):
        try:
            url_path = request.url.path
            if any(url_path.startswith(path) for path in ['/forms']):
                session_id = request.cookies.get('sid')
                user = await redis_client.get(f'session:{session_id}')
                if not user:
                    raise HTTPException(
                        401, 'Please login to access this route')
                request.state.user = json.loads(user)
            return await call_next(request)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        except Exception as exc:
            print(f'Middleware error: {exc}')
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred"}
            )
