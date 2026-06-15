from shared.base_exceptions import BadRequest, NotFound


class ServiceQuestionNotFound(NotFound):
    def __init__(self, detail: str = "Question introuvable."):
        super().__init__(detail=detail)


class ServiceQuestionIndexError(BadRequest):
    def __init__(self, detail: str = "Index d'option invalide."):
        super().__init__(detail=detail)
