import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import config
from shared.db import init_db
from fastapi.middleware.cors import CORSMiddleware
from controllers.appointment_controller import appointments_router
from controllers.auth_controller import auth_router
from controllers.availability_controller import availabilities_router
from controllers.client_controller import clients_router
from controllers.notification_controller import notifications_router
from controllers.payment_controller import payments_router
from controllers.provider_controller import providers_router
from controllers.service_controller import services_router
from shared.error_handlers import register_error_handlers
from shared.logger import setup_logging
from shared.swagger import get_openapi_metadata


def create_app() -> FastAPI:
    setup_logging()
    init_db()

    meta = get_openapi_metadata()
    app = FastAPI(
        title=meta["title"],
        version=meta["version"],
        description=meta["description"],
        openapi_tags=meta["openapi_tags"],
        docs_url="/docs" if config.DOCS_ENABLED else None,
        redoc_url="/redoc" if config.DOCS_ENABLED else None,
        redirect_slashes=False,
    )

    @app.middleware("http")
    async def strip_trailing_slash(request: Request, call_next):
        if request.url.path != "/" and request.url.path.endswith("/"):
            request.scope["path"] = request.url.path.rstrip("/")
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(auth_router)
    app.include_router(clients_router)
    app.include_router(providers_router)
    app.include_router(services_router)
    app.include_router(availabilities_router)
    app.include_router(appointments_router)
    app.include_router(payments_router)
    app.include_router(notifications_router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=config.APP_ENV == "development",
    )
