from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.messages.models import UserMessage


class UserMessageAPITests(APITestCase):
    def setUp(self):
        self.url = reverse('messages-list')

    def test_create_message_success(self):
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone': '+254700000000',
            'message': 'Hello, I would like to know more about your products.',
        }

        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(UserMessage.objects.filter(email=payload['email']).exists())
        self.assertIn('id', response.data)

    def test_missing_fields_returns_400(self):
        response = self.client.post(
            self.url,
            {'name': '', 'email': '', 'message': ''},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))
        self.assertIn('errors', response.data)

    def test_email_failure_does_not_crash(self):
        payload = {
            'name': 'Mailer Error',
            'email': 'broken@example.com',
            'message': 'Testing email failure handling.',
        }

        with patch('apps.messages.views.send_mail', side_effect=Exception('smtp error')):
            response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserMessage.objects.filter(email=payload['email']).exists())
        self.assertFalse(response.data.get('email_sent'))