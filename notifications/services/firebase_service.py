import json
import logging
from django.conf import settings
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

class FirebaseNotificationService:
    """
    Service pour envoyer des notifications push via Firebase Cloud Messaging
    """
    
    @staticmethod
    def send_push_notification(fcm_token, title, body, data=None):
        """
        Envoie une notification push à un appareil spécifique
        """
        try:
            if not fcm_token:
                logger.warning("Aucun FCM token fourni")
                return False

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=fcm_token,
            )

            response = messaging.send(message)
            logger.info(f"Notification envoyée avec succès: {response}")
            return True
            
        except FirebaseError as e:
            logger.error(f"Erreur Firebase: {e}")
            return False
        except ValueError as e:
            logger.error(f"Token FCM invalide: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return False

    @staticmethod
    def send_multiple_notifications(fcm_tokens, title, body, data=None):
        """
        Envoie une notification à plusieurs appareils
        """
        try:
            if not fcm_tokens:
                return {"success_count": 0, "failure_count": 0}

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=fcm_tokens,
            )

            response = messaging.send_multicast(message)
            
            logger.info(
                f"Notifications multicast: {response.success_count} succès, "
                f"{response.failure_count} échecs"
            )
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": response.responses
            }
            
        except Exception as e:
            logger.error(f"Erreur notifications multicast: {e}")
            return {"success_count": 0, "failure_count": len(fcm_tokens)}

    @staticmethod
    def send_to_topic(topic, title, body, data=None):
        """
        Envoie une notification à tous les abonnés d'un topic
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )

            response = messaging.send(message)
            logger.info(f"Notification topic envoyée: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur notification topic: {e}")
            return False

    @staticmethod
    def subscribe_to_topic(fcm_tokens, topic):
        """
        Abonne des appareils à un topic 
        """
        try:
            response = messaging.subscribe_to_topic(fcm_tokens, topic)
            logger.info(
                f"Abonnement topic: {response.success_count} succès, "
                f"{response.failure_count} échecs"
            )
            return response
            
        except Exception as e:
            logger.error(f"Erreur abonnement topic: {e}")
            return None

    @staticmethod
    def unsubscribe_from_topic(fcm_tokens, topic):
        """
        Désabonne des appareils d'un topic
        """
        try:
            response = messaging.unsubscribe_from_topic(fcm_tokens, topic)
            logger.info( 
                f"Désabonnement topic: {response.success_count} succès, "
                f"{response.failure_count} échecs"
            )
            return response
            
        except Exception as e:
            logger.error(f"Erreur désabonnement topic: {e}")
            return None