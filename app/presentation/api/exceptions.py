from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from authx.exceptions import (
    JWTDecodeError,
    MissingTokenError,
)
from presentation.api.schemas import ApiResponse

from application.base.exception import LogicException
from domain.base.exceptions import (
    ApplicationException,
    DomainException,
)
from domain.users.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserException,
    UserNotFoundException,
)


async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
) -> JSONResponse:
    if isinstance(exc, LogicException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, DomainException):
        if isinstance(exc, UserException):
            if isinstance(exc, (InvalidCredentialsException, UserNotFoundException)):
                status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, UserAlreadyExistsException):
                status_code = status.HTTP_409_CONFLICT
            else:
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    response = ApiResponse(
        errors=[{"message": exc.message, "type": exc.__class__.__name__}],
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


async def authx_exception_handler(
    request: Request,
    exc: MissingTokenError | JWTDecodeError,
) -> JSONResponse:
    response = ApiResponse(
        errors=[{"message": str(exc), "type": exc.__class__.__name__}],
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=response.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        error_type = error.get("type", "validation_error")
        errors.append(
            {
                "message": f"{loc}: {msg}",
                "type": error_type,
            },
        )

    response = ApiResponse(
        errors=errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    response = ApiResponse(
        errors=[{"message": str(exc), "type": exc.__class__.__name__}],
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        ApplicationException,
        application_exception_handler,
    )
    app.add_exception_handler(
        MissingTokenError,
        authx_exception_handler,
    )
    app.add_exception_handler(
        JWTDecodeError,
        authx_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        general_exception_handler,
    )
