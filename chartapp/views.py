# from django.shortcuts import render
# from core.models import Product
# # Create your views here.
# def index(request):
#     products = Product.objects.all
    
#     context = {
#         "products": products
#     }
    
#     return render(request, 'chartapp/index.html',context)

from django.shortcuts import render
from django.db.models import Sum
from core.models import Product

def dashboard_view(request):
    products = Product.objects.all()
    total_products = products.count()
    total_stock = products.aggregate(total=Sum('stock'))['total'] or 0
    out_of_stock = products.filter(stock=0).count()
    top_product = products.order_by('-stock').first()

    context = {
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'out_of_stock': out_of_stock,
        'top_product': top_product,
    }
    return render(request, 'chartapp/index.html',context)