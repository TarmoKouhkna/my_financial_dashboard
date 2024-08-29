from django.contrib import admin
from django.urls import path, include
from portfolio.views import CustomLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),  # Use custom logout view
    path('accounts/', include('django.contrib.auth.urls')),  # Include other auth URLs
    path('', include('portfolio.urls')),
]
