import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shared.base_exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erreur inattendue : %s", exc)
        return JSONResponse(status_code=500, content={"error": "Une erreur interne s'est produite."})
