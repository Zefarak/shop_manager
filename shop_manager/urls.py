from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from frontend.demo_views import RestaurantHomepageView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('admin/catelogue/auto-complete/', include('catalogue.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('site-settings/', include('site_settings.urls')),
    path('point-of-sale/', include('point_of_sale.urls')),
    path('point-of-sale/cart/', include('cart.urls')),
    path('reports/', include('report.urls')),
    path('', include('accounts.urls')),

    path('api/', include('shop_manager.api_urls')),


    #  demo urls
    path('demo/', RestaurantHomepageView.as_view(), name='demo_homeage')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USE_WAREHOUSE:
    urlpatterns += [path('warehouse/', include('warehouse.urls')), ]