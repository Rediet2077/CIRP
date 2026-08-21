from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class NotificationListView(APIView):
    """
    Real notification list endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        from .models import Notification
        user = request.user
        if user and not user.is_anonymous:
            qs = Notification.objects.filter(user=user).order_by('-created_at')
        else:
            qs = Notification.objects.all().order_by('-created_at')
            
        data = [{
            'id': str(n.id),
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        } for n in qs[:50]]
        
        unread_count = sum(1 for item in data if not item['is_read'])
        
        return Response({
            'success': True,
            'message': 'Notifications retrieved successfully',
            'data': data,
            'unread_count': unread_count,
            'count': len(data),
            'next': None,
            'previous': None,
        }, status=status.HTTP_200_OK)


class NotificationDeleteView(APIView):
    """
    Delete a single notification
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            
            logger.info(f"Notification {notification_id} deleted by user {request.user.id}")
            
            return Response({
                'success': True,
                'message': 'Notification deleted successfully',
            }, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Notification not found or you do not have permission to delete it',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to delete notification',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationClearAllView(APIView):
    """
    Clear all notifications for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from .models import Notification
        try:
            deleted_count, _ = Notification.objects.filter(user=request.user).delete()
            
            logger.info(f"User {request.user.id} cleared {deleted_count} notifications")
            
            return Response({
                'success': True,
                'message': f'{deleted_count} notifications cleared successfully',
                'deleted_count': deleted_count,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error clearing notifications for user {request.user.id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to clear notifications',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
