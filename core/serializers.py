from rest_framework import serializers
from .models import User, Product, Cart, CartItem, Order, OrderItem, Category
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    class Meta:
        model = User
        fields = ['email', 'password', 'phone_number', 'address', 'first_name', 'last_name', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # Add more custom password validation here if necessary
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise ValidationError("Password must contain at least one letter.")
        return value
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProductSerializer(serializers.ModelSerializer):
    price_after_discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_price_after_discount(self, obj):
        discount_amount = obj.price * (obj.discount_percentage / 100)
        return obj.price - discount_amount

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields =  ['id','quantity']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid email or password"]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["This account is inactive."]
            })

        data['user'] = user
        return data