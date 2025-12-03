"""URL configuration for core project (Kikuyu Vocab Platform)"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.conf import settings

# Customize admin site branding
admin.site.site_header = "DOMINIUM // CONTROL INTERFACE"
admin.site.site_title = "DOMINIUM Admin"
admin.site.index_title = "System Control Panel"

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Public vocab platform (main feature)
    path('vocab/', include('vocab.urls')),

    # Redirect homepage to vocab
    path('', RedirectView.as_view(url='/vocab/', permanent=False), name='home'),
]

# Media files (user uploads: audio, images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

