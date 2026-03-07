from fastapi import status

class ModelAlreadyExistsException(BaseException):
    """Объект уже существует"""

class ModelNoFoundException(BaseException):
    """Объект не найден"""

class ModelMultipleResultsFoundException(BaseException):
    """При ожидании одного объекта нашлось несколько экземпляров"""

class UserNoFoundException(ModelNoFoundException):
    """Пользователь не найден"""

    detail = "User no found with this email"

class UserAlreadyExistsException(ModelAlreadyExistsException):
    """Пользователь уже существует"""

    detail = "User already exists with this email"

class TokenUserNoFoundException(ModelNoFoundException):
    """Токен не найден в бд"""

    detail = "Token user no found"

class TokenUserAlreadyExistsException(ModelAlreadyExistsException):
    """Токен уже существует"""

    detail = "Token user already exists with this user"

class GoalNoFoundException(ModelNoFoundException):
    """Цель не найдена в бд"""

    detail = "Goal no found"

class GoalStageNoFoundException(ModelNoFoundException):
    """Стадия не найдена в бд"""

    detail = "Goal stage no found"

class GoalStageAlreadyExistsException(ModelAlreadyExistsException):
    """Стадия уже существует"""

    detail = "Goal stage already exists"

class ForbiddenException(BaseException):
    """Нет доступа"""

    detail = "Forbidden"

class InvalidStageDependencyException(ModelNoFoundException):
    """Стадии не найдены"""

    detail = "Invalid stage dependency. One or more stages do not exist."
    status_code = status.HTTP_400_BAD_REQUEST

class APIException(Exception):
    def __init__(self, status_code: int, error: str):
        self.status_code = status_code
        self.error = error
