from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id,
                                                           defaults={'quantity': quantity})
            if not created:
                item.quantity = item.quantity + quantity
                item.save()

        return Response({'message': 'added', 'item': CartItemSerializer(item).data})


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(request.data.get('quantity', item.quantity))
        if quantity <= 0:
            item.delete()
            return Response({'message': 'deleted'})

        item.quantity = quantity
        item.save()
        return Response({'item': CartItemSerializer(item).data})

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response({'message': 'deleted'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class MergeCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Merge guest cart into authenticated user's cart.
        Expected payload: { items: [{product_id, quantity}, ...] }
        """
        payload_items = request.data.get('items', [])
        if not isinstance(payload_items, list):
            return Response({'error': 'Invalid items'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            for it in payload_items:
                pid = it.get('product_id')
                qty = int(it.get('quantity', 1))
                if not pid:
                    continue
                obj, created = CartItem.objects.get_or_create(cart=cart, product_id=pid,
                                                              defaults={'quantity': qty})
                if not created:
                    obj.quantity = obj.quantity + qty
                    obj.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)
