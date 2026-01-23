"""order receptions urls."""

from django.urls import path
from orderReceptions import views

app_name = "orderReceptions"


urlpatterns = [
    path(
        "orderreceptions/",
        views.OrderDetailListView.as_view(),
        name="orderreceptions-list",
    ),
    path(
        "orderreceptions/<uuid:pk>/",
        views.OrderDetailView.as_view(),
        name="orderreceptions-detail",
    ),
]
