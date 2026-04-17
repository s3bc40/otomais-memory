from django.views.generic import ListView

from .models import Equipment, ItemType


class EquipmentListView(ListView):
    model = Equipment
    template_name = "encyclopedia/equipment_list.html"
    context_object_name = "equipment_list"
    paginate_by = 24

    def get_queryset(self):
        qs = Equipment.objects.select_related("item_type").order_by("level", "name")
        q = self.request.GET.get("q", "").strip()
        type_id = self.request.GET.get("type", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        if type_id:
            qs = qs.filter(item_type__ankama_id=type_id)
        return qs

    def get_context_data(self, **kwargs: object) -> dict:
        ctx = super().get_context_data(**kwargs)
        ctx["item_types"] = ItemType.objects.order_by("name")
        ctx["current_q"] = self.request.GET.get("q", "")
        ctx["current_type"] = self.request.GET.get("type", "")
        return ctx
