from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from buzukina import settings
from main.views import pageNotFound

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("api/", include("api.urls")),
]

handler404 = pageNotFound

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)