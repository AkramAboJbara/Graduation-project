from django.http import JsonResponse
import django_filters
from rest_framework import status, filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from django_filters import rest_framework as filters

from .models import *
from .serializers import * 
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework import filters


def homepage(request):
    return JsonResponse({"message": "Welcome to the E-commerce Backend API!"})

"""
class HomepageProductAPIView(APIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get(self, request):
        products = Product.objects.all()
        if 'search' in request.query_params:
            search_term = request.query_params['search']
            products = products.filter(name__icontains=search_term)
        if 'category' in request.query_params:
            category = request.query_params['category']
            products = products.filter(category__icontains=category)
        if 'price_min' in request.query_params:
            price_min = request.query_params['price_min']
            products = products.filter(price__gte=price_min)
        if 'price_max' in request.query_params:
            price_max = request.query_params['price_max']
            products = products.filter(price__lte=price_max)
        page = request.GET.get('page', 1) 
        paginator = Paginator(products, 20)
        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)  
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages) 

        serializer = ProductSerializer(paginated_products, many=True)

        return Response({
            'total_pages': paginator.num_pages,
            'current_page': paginated_products.number,
            'products': serializer.data
        }, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        search_filter = filters.SearchFilter()
        return search_filter.filter_queryset(self.request, queryset, self)
"""

authentication_classes = [TokenAuthentication]    

class viewsets_product(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = request.query_params.get('page', 1)  # get the page number from the request
        paginator = Paginator(queryset, 20)  # show 20 items per page

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)  
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)  # if page is out of range, deliver last page

        serializer = self.get_serializer(paginated_products, many=True)

        return Response({
            'total_pages': paginator.num_pages,
            'current_page': paginated_products.number,
            'products': serializer.data
        }, status=status.HTTP_200_OK)


class viewsets_category(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description']
    lookup_field = 'slug'





#@login_required
class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))  # quantity should be an integer

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # validate stock
        if product.stock < quantity:
            return Response(
                {"error": f"Not enough stock available. Only {product.stock} items left."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            # check if the updated quantity exceeds the stock
            if product.stock < (cart_item.quantity + quantity):
                return Response(
                    {"error": f"Not enough stock available. Only {product.stock} items left."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        # decrease the product stock
        product.stock -= quantity
        product.save()

        # recalculate the cart total based on all items in the cart
        cart_items = CartItem.objects.filter(cart=cart)
        cart.total = sum(Decimal(str(item.product.price)) * Decimal(str(item.quantity)) for item in cart_items)
        cart.save()
        serializer = CartItemSerializer(cart_item)
        return Response(
            {
                "cart_item": serializer.data,
                "total_price": float(cart.total)  # convert decimal to float 
            },
            status=status.HTTP_201_CREATED
        )
    
    
class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity_to_remove = int(request.data.get('quantity', 1))  #quantity should be an integer

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        if not cart.items.exists():
            return Response({"error": "Cart is empty. No items to remove."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({"error": "Product not found in the cart"}, status=status.HTTP_404_NOT_FOUND)

        if quantity_to_remove > cart_item.quantity: # validate the quantity to remove
            return Response(
                {"error": f"Cannot remove more than {cart_item.quantity} items."},
                status=status.HTTP_400_BAD_REQUEST
            )
        product.stock += quantity_to_remove # update the product stock
        product.save()
        if quantity_to_remove == cart_item.quantity:
            cart_item.delete() # remove the entire item from the cart
        else:
            cart_item.quantity -= quantity_to_remove
            cart_item.save()

        # recalculate the cart total based on all items in the cart
        cart_items = CartItem.objects.filter(cart=cart)
        cart.total = sum(Decimal(str(item.product.price)) * Decimal(str(item.quantity)) for item in cart_items)
        cart.save()

        return Response(
            {
                "message": "Product quantity updated in cart",
                "total_price": float(cart.total)  # convert decimal to float for response
            },
            status=status.HTTP_200_OK
        )
    

class ViewCartContentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"message": "No cart exists for this user."},
                status=status.HTTP_200_OK
            )
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        response_data = {
            "total_price": float(total_price),  
            "products": [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price * item.quantity),   #convert decimal to float
                    "image": item.product.image.url if item.product.image else None  
                }
                for item in cart_items
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)  
    
    
class HomepageAPIView(APIView):
    def get(self, request):
        
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
