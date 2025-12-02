from .firebase import db

def inventario_panel(request):
    items = db.collection("inventario").stream()
    datos = [i.to_dict() for i in items]
    return {"inventario_panel": datos}
