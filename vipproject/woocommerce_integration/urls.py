# woocommerce_integration/urls.py
from django.urls import path
from .views import sync_orders, view_orders, update_gift, index, update_order_statuses
from django.contrib.auth.views import LogoutView
from .views import IndexView, CustomLoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sync-orders/', sync_orders, name='sync_orders'),
    path('view-orders/', view_orders, name='view_orders'),
    path('update-gift/<int:order_id>/', update_gift, name='update_gift'),
    path('update-gift/', update_gift, name='update_gift_without_id'),
    path('update-order-statuses/', update_order_statuses, name='update_order_statuses'),
    path('index/', IndexView.as_view(), name='index'),  # Protected by LoginRequiredMixin
    path('login/', CustomLoginView.as_view(), name='custom_login'),  # Custom login view
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', IndexView.as_view(), name='root'),  # Add this line for the root path
]

# Add static and media URL patterns only in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
