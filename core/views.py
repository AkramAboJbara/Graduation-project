from django.http import JsonResponse
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.filters import SearchFilter
from .models import Category, Product, User
from .serializers import CategorySerializer, ProductSerializer, UserSerializer ,LoginSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage




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
    
    
class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
authentication_classes = [TokenAuthentication]    