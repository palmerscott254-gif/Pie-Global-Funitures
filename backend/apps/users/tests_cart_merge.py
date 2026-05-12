from django.test import TestCase
from rest_framework.test import APIClient

from apps.cart.models import Cart, CartItem
from apps.users.models import User


class LoginCartMergeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name='Cart User',
            email='cartuser@example.com',
            password='StrongPass123!',
        )

    def test_login_merges_guest_cart_items_into_persistent_cart(self):
        response = self.client.post(
            '/api/users/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
                'cart': {
                    'items': [
                        {'product_id': 101, 'quantity': 2},
                        {'product_id': 202, 'quantity': 1},
                    ]
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        cart = Cart.objects.get(user=self.user)
        item_101 = CartItem.objects.get(cart=cart, product_id=101)
        item_202 = CartItem.objects.get(cart=cart, product_id=202)

        self.assertEqual(item_101.quantity, 2)
        self.assertEqual(item_202.quantity, 1)

    def test_login_merges_quantities_when_product_already_exists(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product_id=101, quantity=1)

        response = self.client.post(
            '/api/users/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
                'cart': [{'product_id': 101, 'quantity': 3}],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        item_101 = CartItem.objects.get(cart=cart, product_id=101)
        self.assertEqual(item_101.quantity, 4)
