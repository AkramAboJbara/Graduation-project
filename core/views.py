from django.http import JsonResponse
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.filters import SearchFilter
from .models import Cart, Category, OrderItem, Product, User
from .serializers import * 
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Product, CartItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

def homepage(request):
    return JsonResponse({"message": "Welcome to the E-commerce Backend API!"})


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


authentication_classes = [TokenAuthentication]    

class viewsets_product(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description']
    
class viewsets_category(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description']





#@login_required
class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < int(quantity):
            return Response(
                {"error": f"Not enough stock available, Only {product.stock} items left."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=user)

        # get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if product.stock < (cart_item.quantity + int(quantity)):
                return Response(
                    {"error": f"Not enough stock available. Only {product.stock} items left."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()
        # decrease the product stock
        product.stock -= int(quantity)
        product.save()
        # update the cart total
        cart.total += product.price * int(quantity)
        cart.save()
        serializer = CartItemSerializer(cart_item)
        return Response(
            {
                "cart_item": serializer.data,
                "total_price": cart.total
            },
            status=status.HTTP_201_CREATED
        )
    
    
class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity_to_remove = request.data.get('quantity', 1)  # default to 1 if not provided

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

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({"error": "Product not found in the cart"}, status=status.HTTP_404_NOT_FOUND)

        # validate the quantity to remove
        if quantity_to_remove > cart_item.quantity:
            return Response(
                {"error": f"Cannot remove more than {cart_item.quantity} items."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # update the cart total
        cart.total -= product.price * int(quantity_to_remove)
        cart.save()

        # update the product stock
        product.stock += int(quantity_to_remove)
        product.save()
        if quantity_to_remove == cart_item.quantity:
            # remove the entire item from the cart
            cart_item.delete()
        else:
            # decrease the quantity in the cart
            cart_item.quantity -= int(quantity_to_remove)
            cart_item.save()
        return Response(
            {
                "message": "Product quantity updated in cart",
                "total_price": cart.total
            },
            status=status.HTTP_200_OK
        )