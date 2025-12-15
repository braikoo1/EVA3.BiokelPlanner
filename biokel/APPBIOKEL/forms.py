from django import forms

TIPOS_INVENTARIO = [
    ("algas", "Algas"),
    ("calcio", "Calcio"),
    ("alimento", "Alimento"),
    ("huevos", "Huevos"),
]

class InventarioForm(forms.Form):
    tipo = forms.ChoiceField(choices=TIPOS_INVENTARIO)
    cantidad = forms.FloatField(min_value=0.01)

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero")
        return cantidad