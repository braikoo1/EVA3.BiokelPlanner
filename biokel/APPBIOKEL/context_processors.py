from .models import InventarioItem

def inventario_context(request):
    items = InventarioItem.objects.all().order_by('nombre')
    return {'inventario_panel': items}
