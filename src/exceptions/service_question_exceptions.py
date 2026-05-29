from shared.base_exceptions import NotFound


class ServiceQuestionNotFound(NotFound):
    def __init__(self, detail: str = "Question introuvable."):
        super().__init__(detail=detail)
