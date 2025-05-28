from django.shortcuts import render
from django.db.models import Sum, Count
from core.models import Product

def dashboard_view(request):
    products = Product.objects.all()
    total_products = products.count()
    total_stock = products.aggregate(total=Sum('stock'))['total'] or 0
    out_of_stock = products.filter(stock=0).count()
    top_product = products.order_by('-stock').first()

    category_counts = Product.objects.values('category__name').annotate(total=Count('id'))
    category_total = sum(item['total'] for item in category_counts)
    category_names_count = category_counts.count()
    
    top_selling = Product.objects.order_by('-sales')[:10] 
    total_sales = Product.objects.aggregate(total=Sum('sales'))['total'] or 0
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'out_of_stock': out_of_stock,
        'top_product': top_product,
        'category_counts': category_counts,
        'category_total': category_total,
        'category_names_count': category_names_count,
        'top_selling': top_selling,
        'total_sales': total_sales,
    }
    return render(request, 'chartapp/index.html',context)

