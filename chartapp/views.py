from django.shortcuts import render
from django.db.models import Sum, Count
from core.models import Product
from django.http import HttpResponse
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from core.models import Category, Product
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import user_passes_test


superuser_required = user_passes_test(
    lambda u: u.is_superuser,
    login_url='/admin/login/' 
)


@superuser_required
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

@superuser_required
def product_list_view(request):
    # Get all categories and their associated products
    categories = Category.objects.all().prefetch_related('products')

    # Check if a specific category is requested
    category_id = request.GET.get('category')
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            products = category.products.all()
        except Category.DoesNotExist:
            products = []
    else:
        products = Product.objects.all()

    # Context for rendering the template
    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'product_list.html', context)

@superuser_required
def export_csv(request):
    products = Product.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['Category', 'Product Name', 'Price', 'Stock', 'Sales'])
    for product in products:
        writer.writerow([
            product.category.name,
            product.name,
            product.price,
            product.stock,
            product.sales,
        ])

    return response

@superuser_required
def export_pdf(request):
    products = Product.objects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="products.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 50, "Product List")

    x, y = 50, height - 80
    p.drawString(x, y, "Category")
    p.drawString(x + 150, y, "Product Name")
    p.drawString(x + 300, y, "Price")
    p.drawString(x + 400, y, "Stock")
    p.drawString(x + 500, y, "Sales")

    y -= 20
    for product in products:
        p.drawString(x, y, str(product.category.name))
        p.drawString(x + 150, y, str(product.name))
        p.drawString(x + 300, y, str(product.price))
        p.drawString(x + 400, y, str(product.stock))
        p.drawString(x + 500, y, str(product.sales))
        y -= 20
    p.showPage()
    p.save()

    return response

@superuser_required
def sales_summary_view(request):
    today = now()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)
    weekly_sales = Product.objects.filter(date_sold__gte=one_week_ago).count()
    monthly_sales = Product.objects.filter(date_sold__gte=one_month_ago).count()
    annual_sales = Product.objects.filter(date_sold__gte=one_year_ago).count()
    total_sales = Product.objects.filter(date_sold__isnull=False).count()
    context = {
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'annual_sales': annual_sales,
        'total_sales': total_sales,
    }

    return render(request, 'sales_summary.html', context)


def export_sales_csv(queryset, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Price', 'Category', 'Date Sold'])

    for product in queryset:
        writer.writerow([
            product.name,
            product.price,
            product.category.name,
            product.date_sold,
        ])

    return response


def export_sales_pdf(queryset, title, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica", 16)
    p.drawString(50, height - 50, title)

    # Headers
    x, y = 50, height - 80
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x, y, "* Product Name * :")
    p.drawString(x + 200, y, " Price ")
    p.drawString(x + 350, y, " Category ")
    p.drawString(x + 500, y, " Date Sold ")

    # Data rows
    for product in queryset:
        y -= 20
        if y < 50:  
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)
        p.drawString(x, y, str(product.name))
        p.drawString(x + 200, y, str(product.price))
        p.drawString(x + 350, y, str(product.category.name))
        p.drawString(x + 500, y, str(product.date_sold))

    p.showPage()
    p.save()

    return response


# Weekly Sales Export Functions
@superuser_required
def export_weekly_sales_csv(request):
    today = now()
    one_week_ago = today - timedelta(days=7)
    weekly_sales = Product.objects.filter(date_sold__gte=one_week_ago)
    return export_sales_csv(weekly_sales, "weekly_sales")
def export_weekly_sales_pdf(request):
    today = now()
    one_week_ago = today - timedelta(days=7)
    weekly_sales = Product.objects.filter(date_sold__gte=one_week_ago)
    return export_sales_pdf(weekly_sales, "Weekly Sales", "weekly_sales")


# Monthly Sales Export Functions
@superuser_required
def export_monthly_sales_csv(request):
    today = now()
    one_month_ago = today - timedelta(days=30)
    monthly_sales = Product.objects.filter(date_sold__gte=one_month_ago)
    return export_sales_csv(monthly_sales, "monthly_sales")

@superuser_required
def export_monthly_sales_pdf(request):
    today = now()
    one_month_ago = today - timedelta(days=30)
    monthly_sales = Product.objects.filter(date_sold__gte=one_month_ago)
    return export_sales_pdf(monthly_sales, "Monthly Sales", "monthly_sales")


# Annual Sales Export Functions
@superuser_required
def export_annual_sales_csv(request):
    today = now()
    one_year_ago = today - timedelta(days=365)
    annual_sales = Product.objects.filter(date_sold__gte=one_year_ago)
    return export_sales_csv(annual_sales, "annual_sales")

@superuser_required
def export_annual_sales_pdf(request):
    today = now()
    one_year_ago = today - timedelta(days=365)
    annual_sales = Product.objects.filter(date_sold__gte=one_year_ago)
    return export_sales_pdf(annual_sales, "Annual Sales", "annual_sales")


# Forever Sales Export Functions
@superuser_required
def export_forever_sales_csv(request):
    forever_sales = Product.objects.filter(date_sold__isnull=False)
    return export_sales_csv(forever_sales, "forever_sales")

@superuser_required
def export_forever_sales_pdf(request):
    forever_sales = Product.objects.filter(date_sold__isnull=False)
    return export_sales_pdf(forever_sales, "Forever Sales", "forever_sales")

