from django.urls import path
from . import views

urlpatterns = [path("", views.ChartsView.as_view(), name="plot")]