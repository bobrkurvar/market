import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from adapters.cookies import AuthCookies
from domain.exceptions import (AlreadyExistsError, CredentialsValidateError,
                               ForeignKeyViolationError, NotFoundError,
                               UnauthorizedError, UserLoginNotFoundError)

log = logging.getLogger(__name__)


async def not_found_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)
    return JSONResponse(
        status_code=404, content={"detail": "Запрашиваемый ресурс не найден"}
    )


async def already_exists_handler(request: Request, exc: AlreadyExistsError):
    log.error("Ошибка создания в базе данных: %s", exc)
    return JSONResponse(
        status_code=409, content={"detail": "Такая запись уже существует"}
    )


async def foreign_key_handler(request: Request, exc: ForeignKeyViolationError):
    log.error("Ошибка создания внешнего ключа: %s", exc)
    return JSONResponse(
        status_code=409, content={"detail": "Указанный связанный ресурс не существует"}
    )


async def admin_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка админки: %s", exc)
    return JSONResponse(
        status_code=500, content={"detail": "Внутренняя ошибка сервера"}
    )


async def global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return JSONResponse(
        status_code=500, content={"detail": "Произошла непредвиденная ошибка"}
    )


async def invalid_tokens_or_not_exists_handler(
    request: Request, exc: UnauthorizedError
):
    log.debug("tokens error: %s", exc)
    response = JSONResponse(
        status_code=401,
        content={"detail": "Сессия истекла, пожалуйста, войдите заново"},
    )
    cookie_manager = AuthCookies()
    cookie_manager.clear_tokens(response)
    return response


async def user_login_not_found_error_handler(
    request: Request, exc: UserLoginNotFoundError
):
    log.error("user not found: %s", exc)
    response = JSONResponse(
        status_code=401, content={"detail": "Пользователь с таким логином не найден"}
    )
    # cookie_manager = AuthCookies()
    # cookie_manager.clear_tokens(response)
    return response


async def invalid_credentials_error_handler(
    request: Request, exc: CredentialsValidateError
):
    log.error("invalid credentials: %s", exc)
    response = JSONResponse(status_code=401, content={"detail": "Неверный пароль"})
    # cookie_manager = AuthCookies()
    # cookie_manager.clear_tokens(response)
    return response
