from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from apps.messages.models import UserMessage
from apps.notifications.models import Notification, NotificationType
from apps.orders.models import Order
from apps.users.models import User


class NotificationSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Signal User',
            email='signal@example.com',
            password='StrongPass123!',
        )

    def _create_order(self, status='pending'):
        return Order.objects.create(
            name='Signal User',
            email=self.user.email,
            phone='0700000000',
            address='Nairobi',
            city='Nairobi',
            postal_code='00100',
            items=[{'product_id': 1, 'name': 'Chair', 'qty': 1, 'price': 100}],
            total_amount=Decimal('100.00'),
            status=status,
        )

    @patch('apps.notifications.notification_service.NotificationService.broadcast_unread_count_update')
    @patch('apps.notifications.notification_service.NotificationService.broadcast_notification')
    def test_pending_to_received_creates_single_order_received_notification(self, _mock_broadcast, _mock_unread):
        order = self._create_order(status='pending')

        order.status = 'received'
        order.save()

        self.assertEqual(
            Notification.objects.filter(
                user=self.user,
                title='Order Received',
            ).count(),
            1,
        )

        order.status = 'received'
        order.save()

        self.assertEqual(
            Notification.objects.filter(
                user=self.user,
                title='Order Received',
            ).count(),
            1,
        )

    @patch('apps.notifications.notification_service.NotificationService.broadcast_unread_count_update')
    @patch('apps.notifications.notification_service.NotificationService.broadcast_notification')
    def test_received_to_shipped_creates_shipped_notification(self, _mock_broadcast, _mock_unread):
        order = self._create_order(status='received')

        order.status = 'shipped'
        order.save()

        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                notification_type=NotificationType.ORDER_SHIPPED,
            ).exists()
        )

    @patch('apps.notifications.notification_service.NotificationService.broadcast_unread_count_update')
    @patch('apps.notifications.notification_service.NotificationService.broadcast_notification')
    def test_out_for_delivery_creates_delivery_update_notification(self, _mock_broadcast, _mock_unread):
        order = self._create_order(status='shipped')

        order.status = 'out_for_delivery'
        order.save()

        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                notification_type=NotificationType.DELIVERY_UPDATE,
            ).exists()
        )

    @patch('apps.notifications.notification_service.NotificationService.broadcast_unread_count_update')
    @patch('apps.notifications.notification_service.NotificationService.broadcast_notification')
    def test_admin_reply_creates_support_reply_notification(self, _mock_broadcast, _mock_unread):
        msg = UserMessage.objects.create(
            name='Signal User',
            email=self.user.email,
            phone='0700000000',
            message='I need help with my order.',
            status='new',
        )

        msg.reply_text = 'Thanks for contacting us. Your order is now being processed.'
        msg.status = 'replied'
        msg.save()

        notification = Notification.objects.filter(
            user=self.user,
            notification_type=NotificationType.ADMIN_MESSAGE,
        ).latest('created_at')

        self.assertEqual(notification.title, 'You have received a reply from support.')
        self.assertIn('Thanks for contacting us', notification.message)
        self.assertEqual(notification.metadata.get('message_id'), msg.id)
