class AppException(Exception):
    status_code: int = 500

    def __init__(self, detail: str = "Une erreur est survenue."):
        self.detail = detail
        super().__init__(detail)


class BadRequest(AppException):
    status_code = 400


class Unauthorized(AppException):
    status_code = 401


class Forbidden(AppException):
    status_code = 403


class NotFound(AppException):
    status_code = 404


class Conflict(AppException):
    status_code = 409


class UnprocessableEntity(AppException):
    status_code = 422


class InternalServerError(AppException):
    status_code = 500
