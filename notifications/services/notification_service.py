from django.contrib.auth import get_user_model
from .firebase_service import FirebaseNotificationService
from firebase_admin.exceptions import FirebaseError
from notifications.models import DeviceFcmToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

logger = logging.getLogger(__name__)

class NotificationService:  
    """
    Service central pour gérer toutes les notifications
    """

    @staticmethod
    def _send_in_app_notification(notification):
        """
        CORRIGÉ : Envoie au groupe PRIVÉ de l'utilisateur pour un badge précis.
        """
        try:
            channel_layer = get_channel_layer()
            
            # Utilise l'ID de l'utilisateur de la notification !
            # Cela doit correspondre EXACTEMENT au nom dans ton Consumer
            user_group_name = f"user_{notification.user.id}"
            
            from ..serializers import NotificationSerializer
            serialized_notification = NotificationSerializer(notification).data
            
            # On envoie UNIQUEMENT à cet utilisateur
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'send_new_detection', 
                    'content': serialized_notification
                }
            )
            
            logger.info(f"Notification {notification.id} envoyée au groupe privé {user_group_name}")
            return True
                    
        except Exception as e:
            logger.error(f"Erreur envoi WebSocket: {e}")
            return False


    """
    @staticmethod
    def _send_in_app_notification(notification):
        
        CORRIGÉ : Envoie au groupe GLOBAL que le mobile écoute vraiment.
    
        try:
            channel_layer = get_channel_layer()
          
            global_group_name = 'security_alerts'
            
            from ..serializers import NotificationSerializer
            serialized_notification = NotificationSerializer(notification).data
            
            # On envoie à TOUT le groupe 'security_alerts'
            async_to_sync(channel_layer.group_send)(
                global_group_name,
                {
                    # 'type' doit correspondre au nom de la fonction dans ton Consumer :
                    # send_new_detection -> va appeler async def send_new_detection(...)
                    'type': 'send_new_detection', 
                    'content': serialized_notification
                }
            )
            
            logger.info(f"Notification {notification.id} diffusée sur security_alerts")
            return True
                    
        except Exception as e:
            logger.error(f"Erreur envoi WebSocket: {e}")
            return False
            """
    
    @staticmethod
    def _send_push_notification(notification, user):
        """
        Envoie une notification push groupée (Multicast) à tous les appareils de l'utilisateur
        """
        try:
            # Récupération de tous les tokens de l'utilisateur d'un coup
            devices = DeviceFcmToken.objects.filter(user=user)
            
            if not devices.exists():
                logger.info(f"Utilisateur {user.id} n'a aucun device FCM enregistré.")
                notification.status = 'skipped'
                notification.save()
                return False

            # On extrait les tokens dans une liste simple
            tokens = list(devices.values_list('fcm_token', flat=True))

            notification_data = {
                'notification_id': str(notification.id),
                'detection_event_id': str(notification.detection_event_id) if notification.detection_event_id else "",
                'channel': 'push',
                'title': notification.title,
                'message': notification.message,
                'timestamp': timezone.now().isoformat(),
            }

            # APPEL MULTICAST : On envoie à tous les tokens de l'utilisateur en un seul appel
            result = FirebaseNotificationService.send_multiple_notifications(
                fcm_tokens=tokens,
                title=notification.title,
                body=notification.message,
                data=notification_data
            )

            # Analyse du résultat Multicast
            if result['success_count'] > 0:
                notification.status = 'sent'
                logger.info(f"Push réussi pour {user.username} ({result['success_count']} appareils)")
            else:
                notification.status = 'failed'
                logger.error(f"Échec total du push pour {user.username}")

            notification.sent_at = timezone.now()
            notification.save()
            return result['success_count'] > 0

        except Exception as e:
            logger.error(f"Erreur lors du traitement Multicast pour {notification.id}: {e}")
            notification.status = 'failed'
            notification.save()
            return False

       
    
    @staticmethod
    def _send_email_notification(notification):
        try:
            user = notification.user
            if not user.email:
                return False

            subject = f"{notification.title}"
            
            # CORRECTION : On utilise username ou first_name au lieu de full_name
            # On peut aussi utiliser getattr pour éviter que ça plante si le champ manque
            display_name = getattr(user, 'first_name', user.username)

            message = f"""
            Bonjour {display_name},
            
            {notification.message}
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Email simulé dans la console pour {user.email}")
            return True
                
        except Exception as e:
            # C'est ici que tu voyais l'erreur 'full_name'
            logger.error(f"Erreur envoi email notification: {e}")
            return False
        
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """
        Nettoie les anciennes notifications
        """
        try:
            from ..models import Notification
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            
            deleted_count, _ = Notification.objects.filter(
                created_at__lt=cutoff_date,
                is_read=True
            ).delete()
            
            logger.info(f"{deleted_count} anciennes notifications supprimées")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur nettoyage notifications: {e}")
            return 0
    
    @staticmethod
    def get_unread_count(user_id):
        """
        Retourne le nombre de notifications non lues pour un utilisateur
        """
        try:
            from ..models import Notification
            return Notification.objects.filter(
                user_id=user_id,
                is_read=False,
                channel__in=['in_app', 'all']
            ).count()
            
        except Exception as e:
            logger.error(f"Erreur comptage notifications non lues: {e}")
            return 0 
