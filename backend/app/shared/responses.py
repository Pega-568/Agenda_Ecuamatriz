"""
app/shared/responses.py — Respuestas JSON estandarizadas
Agenda Ecuamatriz

REGLA: Todos los endpoints deben usar estas funciones para responder.
Nunca retornar jsonify() directo desde routes.

Estructura de respuesta exitosa:
{
    "success": true,
    "data": { ... },
    "message": "Descripción opcional"
}

Estructura de respuesta de error:
{
    "success": false,
    "error": {
        "message": "Descripción del error",
        "code": "ERROR_CODE_OPCIONAL",
        "details": { ... }
    }
}
"""

from flask import jsonify
from typing import Any, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200,
    meta: Optional[dict] = None,
):
    """
    Respuesta JSON de operación exitosa.

    Args:
        data: Payload principal de la respuesta.
        message: Mensaje descriptivo opcional.
        status_code: Código HTTP (default 200).
        meta: Metadatos adicionales (paginación, etc.).

    Returns:
        Tuple (Response, status_code) compatible con Flask.
    """
    body = {"success": True}

    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    if meta:
        body["meta"] = meta

    return jsonify(body), status_code


def created_response(data: Any = None, message: str = "Recurso creado exitosamente."):
    """Atajo para respuesta 201 Created."""
    return success_response(data=data, message=message, status_code=201)


def error_response(
    message: str,
    status_code: int = 400,
    code: Optional[str] = None,
    details: Optional[Any] = None,
):
    """
    Respuesta JSON de error.

    Args:
        message: Descripción legible del error.
        status_code: Código HTTP (default 400).
        code: Código de error interno opcional (ej: "ROOM_UNAVAILABLE").
        details: Detalles adicionales del error (errores de validación, etc.).

    Returns:
        Tuple (Response, status_code) compatible con Flask.
    """
    error_body: dict = {"message": message}

    if code:
        error_body["code"] = code
    if details is not None:
        error_body["details"] = details

    return jsonify({"success": False, "error": error_body}), status_code


def validation_error_response(errors: Any):
    """
    Atajo para errores de validación Marshmallow.

    Args:
        errors: Diccionario de errores de Marshmallow.
    """
    return error_response(
        message="Datos de entrada inválidos.",
        status_code=422,
        code="VALIDATION_ERROR",
        details=errors,
    )


def paginated_response(
    data: list,
    total: int,
    page: int,
    per_page: int,
    message: Optional[str] = None,
):
    """
    Respuesta paginada estándar.

    Args:
        data: Lista de ítems de la página actual.
        total: Total de registros en la base de datos.
        page: Página actual (1-indexed).
        per_page: Registros por página.
        message: Mensaje descriptivo opcional.
    """
    import math

    meta = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page) if per_page > 0 else 0,
    }
    return success_response(data=data, message=message, meta=meta)
