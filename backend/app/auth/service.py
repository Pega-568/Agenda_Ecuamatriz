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

        Implementa consulta a BD + bcrypt.check_password_hash().
        """
        if not email or not password:
            return None

        from app.users.service import UserService

        user = UserService.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not UserService.check_password(user, password):
            return None
        return user
