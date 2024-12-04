from rest_framework import serializers
from .models import User, Product, Cart, ShoppingCart, Order, OrderItem, Category
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Mark the password field as write-only

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'address', 'is_active', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)  
        user.set_password(password)  
        user.save() 
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid username or password"]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["This account is inactive."]
            })

        data['user'] = user
        return data