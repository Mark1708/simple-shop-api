from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api import api_router
from src.core.config import settings
from src.model.api_responses import common_responses
from src.util.rate_limit import limiter
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(
    title="Online Shop service",
    description="Provides shop managing REST API.",
    debug=settings.DEBUG,
    responses=common_responses,
    docs_url="/swagger",
    version="0.1.0"
)
app.include_router(api_router)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)