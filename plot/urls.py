from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'plot'
urlpatterns = [
    path("", views.ChartsView.as_view(), name="plot"),
    path("export/", views.csv_export, name="csv_export"),#追記
    path('charts/', views.as_view(), name='charts'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)