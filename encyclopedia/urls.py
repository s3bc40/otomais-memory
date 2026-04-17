from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("equipment/", views.EquipmentListView.as_view(), name="equipment-list"),
    path(
        "equipment/<int:ankama_id>/",
        views.EquipmentDetailView.as_view(),
        name="equipment-detail",
    ),
]
