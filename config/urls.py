from django.contrib import admin
from django.urls import path, include
from users import urls as user_urls
from bookings import urls as booking_urls
from payments import urls as payment_urls

DEFAULT_API_URL = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),

    path(DEFAULT_API_URL, include(user_urls)),
    path(DEFAULT_API_URL, include(booking_urls)),
    path(DEFAULT_API_URL, include(payment_urls))
]
