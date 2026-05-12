from rest_framework import serializers

from apps.products.models import Product
from .models import Cart, CartItem


class CartProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'main_image', 'image')

    def get_image(self, obj):
        request = self.context.get('request')
        if not obj.main_image:
            return None
        try:
            url = obj.main_image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return None


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'quantity', 'product')

    def get_product(self, obj):
        try:
            product = Product.objects.get(id=obj.product_id)
        except Product.DoesNotExist:
            return None
        return CartProductSerializer(product, context=self.context).data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'created_at', 'updated_at', 'items')
