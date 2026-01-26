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
    """У пользователя нет активных целей"""

    detail = "Goal no found with this user"
