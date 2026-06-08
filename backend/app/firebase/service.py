import logging
from flask import current_app
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, messaging
from app.users.models import User, MobileDeviceToken
from app import db

logger = logging.getLogger(__name__)

class FirebaseService:
    """
    Servicio de notificaciones Push de Firebase.
    Se conecta con FCM para enviar notificaciones a dispositivos móviles.
    
    Implementa un patrón 'fail-silent' cuando FCM_ENABLED es False
    para que el sistema funcione localmente sin Firebase configurado.
    """
    
    _initialized = False

    @classmethod
    def _initialize(cls):
        """Inicializa firebase_admin si no lo está y FCM_ENABLED es True."""
        if cls._initialized:
            return

        fcm_enabled = current_app.config.get("FCM_ENABLED", False)
        if not fcm_enabled:
            return

        try:
            creds_path = current_app.config.get("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
            cred = credentials.Certificate(creds_path)
            
            # Verificar si ya existe una app para no inicializar dos veces en tests
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            cls._initialized = True
            logger.info("Firebase Admin inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando Firebase Admin: {str(e)}")
            # Fallar silenciosamente, la app sigue funcionando sin push
            cls._initialized = False

    @classmethod
    def send_push_to_user(cls, user_id: int, title: str, body: str, data: Optional[dict] = None) -> bool:
        """
        Envía una notificación push a todos los dispositivos registrados de un usuario.
        
        Args:
            user_id: ID del usuario destinatario.
            title: Título de la notificación.
            body: Cuerpo del mensaje.
            data: Diccionario opcional de datos adicionales.
            
        Returns:
            True si se envió (o simuló exitosamente), False si hubo error crítico.
        """
        fcm_enabled = current_app.config.get("FCM_ENABLED", False)
        if not fcm_enabled:
            logger.info(f"[SIMULADO FCM] Push a User {user_id}: {title} - {body}")
            return True
            
        cls._initialize()
        if not cls._initialized:
            return False

        tokens = MobileDeviceToken.query.filter_by(user_id=user_id, is_active=True).all()
        if not tokens:
            return False

        success = False
        for token_obj in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    data=data or {},
                    token=token_obj.fcm_token
                )
                messaging.send(message)
                success = True
            except messaging.UnregisteredError:
                # El token ya no es válido, desactivarlo
                token_obj.is_active = False
                db.session.commit()
                logger.info(f"Token FCM revocado automáticamente para usuario {user_id}")
            except Exception as e:
                logger.error(f"Error enviando FCM a usuario {user_id}: {str(e)}")

        return success

    @classmethod
    def send_push_to_many(cls, user_ids: List[int], title: str, body: str, data: Optional[dict] = None) -> bool:
        """
        Envía notificación a múltiples usuarios.
        """
        success = True
        for uid in user_ids:
            # Aunque sea iterativo para simplificar lógica,
            # en un sistema masivo se usaría multicast
            if not cls.send_push_to_user(uid, title, body, data):
                success = False
        return success
