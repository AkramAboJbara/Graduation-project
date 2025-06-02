from django.urls import include, path
from . import views

urlpatterns = [
    path('dashboard-info', views.dashboard_view, name='index'),
    path('dashboard-info/Product_List', views.product_list_view, name='product_list'),
    path('dashboard-info/export/csv/', views.export_csv, name='export_csv'),
    path('dashboard-info/export/pdf/', views.export_pdf, name='export_pdf'),
    path('dashboard-info/sales-summary/', views.sales_summary_view, name='sales_summary'),
    path('dashboard-info/sales-summary/export/weekly/csv/', views.export_weekly_sales_csv, name='export_weekly_sales_csv'),
    path('dashboard-info/sales-summary/export/weekly/pdf/', views.export_weekly_sales_pdf, name='export_weekly_sales_pdf'),
    path('dashboard-info/sales-summary/export/monthly/csv/', views.export_monthly_sales_csv, name='export_monthly_sales_csv'),
    path('dashboard-info/sales-summary/export/monthly/pdf/', views.export_monthly_sales_pdf, name='export_monthly_sales_pdf'),
    path('dashboard-info/sales-summary/export/annual/csv/', views.export_annual_sales_csv, name='export_annual_sales_csv'),
    path('dashboard-info/sales-summary/export/annual/pdf/', views.export_annual_sales_pdf, name='export_annual_sales_pdf'),
    path('dashboard-info/sales-summary/export/forever/csv/', views.export_forever_sales_csv, name='export_forever_sales_csv'),
    path('dashboard-info/sales-summary/export/forever/pdf/', views.export_forever_sales_pdf, name='export_forever_sales_pdf'),
    
]