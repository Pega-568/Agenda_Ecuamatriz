"""
app/auth/service.py — Servicio de autenticación compartido
Agenda Ecuamatriz

Lógica de negocio compartida entre autenticación web (Flask-Login)
y autenticación API (JWT para Android).

Las rutas (session_routes.py y api_routes.py) llaman a estos métodos.
NUNCA poner lógica de negocio en las rutas.

Fase de implementación: Fase 1
"""


class AuthService:
    """
    Servicio de autenticación.

    Métodos planificados (implementar en Fase 1):
        - authenticate(email, password) → User | None
        - change_password(user, old_password, new_password) → bool
        - request_password_reset(email) → token
        - reset_password(token, new_password) → bool
    """

    @staticmethod
    def authenticate(email: str, password: str):
        """
        Verifica credenciales de email/contraseña.

        Args:
            email: Email del usuario.
            password: Contraseña en texto plano.

        Returns:
            User si las credenciales son válidas y el usuario está activo.
            None si son inválidas o el usuario está desactivado.

        TODO (Fase 1): Implementar consulta a BD + bcrypt.check_password_hash()
        """
        raise NotImplementedError("AuthService.authenticate — implementar en Fase 1")
