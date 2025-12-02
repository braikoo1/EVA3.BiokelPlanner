from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .firebase import sumar_inventario
from .firebase import db
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            error = "Usuario o contraseña incorrectos"

    return render(request, "login.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("/login/")

@login_required
def inicio(request):
    return render(request, "inicio.html")

def registrarse(request):
    mensaje = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            if User.objects.filter(username=username).exists():
                mensaje = "Ese usuario ya existe"
            else:
                User.objects.create_superuser(username=username, password=password)
                return redirect("login")
        else:
            mensaje = "Debes ingresar usuario y contraseña"

    return render(request, "registrarse.html", {"mensaje": mensaje})

@login_required
def raciones(request):
    resultados = None

    if request.method == "POST":
        gallinas = int(request.POST.get("gallinas"))

        # Consumo diario
        algas_dia = 5  
        calcio_dia = 7   

        # Dia
        algas_tot_dia = algas_dia * gallinas
        calcio_tot_dia = calcio_dia * gallinas
        mezcla_dia = algas_tot_dia + calcio_tot_dia

        # Semana
        algas_sem = algas_tot_dia * 7
        calcio_sem = calcio_tot_dia * 7
        mezcla_sem = algas_sem + calcio_sem

        # optimizacion del 15%
        mezcla_sem_opt = mezcla_sem * 0.85

        # Mes
        algas_mes = algas_tot_dia * 30
        calcio_mes = calcio_tot_dia * 30
        mezcla_mes = algas_mes + calcio_mes

        mezcla_mes_opt = mezcla_mes * 0.85

        resultados = {
            "gallinas": gallinas,
            "algas_sem": algas_sem,
            "calcio_sem": calcio_sem,
            "mezcla_sem": round(mezcla_sem / 1000, 2),         
            "mezcla_sem_opt": round(mezcla_sem_opt / 1000, 2),  
         
            "algas_mes": algas_mes,
            "calcio_mes": calcio_mes,
            "mezcla_mes": round(mezcla_mes / 1000, 2),
            "mezcla_mes_opt": round(mezcla_mes_opt / 1000, 2),
        }

    return render(request, "raciones.html", {"resultados": resultados})


@login_required
def huevos(request):
    if request.method == "POST":
        fecha = request.POST.get("fecha")
        cantidad = int(request.POST.get("cantidad"))
        db.collection("produccion_huevos").add({
            "fecha": fecha,
            "cantidad": cantidad
        })

        inv_ref = db.collection("inventario").where("tipo", "==", "huevos").stream()
        docs = list(inv_ref)

        if docs:
            doc_id = docs[0].id
            cantidad_actual = docs[0].to_dict().get("cantidad", 0)
            db.collection("inventario").document(doc_id).update({
                "cantidad": cantidad_actual + cantidad
            })
        else:
            db.collection("inventario").add({
                "tipo": "huevos",
                "cantidad": cantidad,
                "unidad": "u"
            })

        return redirect("huevos")
    registros_ref = db.collection("produccion_huevos").stream()
    registros = []

    for r in registros_ref:
        data = r.to_dict()
        registros.append({
            "fecha": data.get("fecha", ""),
            "cantidad": data.get("cantidad", 0)
        })

    return render(request, "huevos.html", {"registros": registros})
@login_required
def reportes(request):
    huevos_ref = db.collection("produccion_huevos").order_by("fecha").stream()

    fechas_huevos = []
    valores_huevos = []

    for h in huevos_ref:
        data = h.to_dict()
        fechas_huevos.append(data.get("fecha", ""))
        valores_huevos.append(data.get("cantidad", 0))

    fechas_raciones = []
    valores_raciones = []

    for i in range(len(fechas_huevos)):
        fechas_raciones.append(fechas_huevos[i])
        valores_raciones.append(valores_huevos[i] * 12) 

    contexto = {
        "fechas_huevos": json.dumps(fechas_huevos),
        "valores_huevos": json.dumps(valores_huevos),
        "fechas_raciones": json.dumps(fechas_raciones),
        "valores_raciones": json.dumps(valores_raciones),
    }

    return render(request, "metricas.html", contexto)


@login_required
def inventario(request):

    from .firebase import sumar_inventario

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        cantidad = request.POST.get("cantidad")

        if tipo and cantidad:
            cantidad = int(cantidad)
            unidad = "g" if tipo in ["algas", "calcio"] else "u"
            sumar_inventario(tipo, cantidad, unidad)

        return redirect("inventario")
    
    productos_ref = db.collection("inventario").stream()
    productos = [p.to_dict() | {"id": p.id} for p in productos_ref]

    return render(request, "inventario.html", {"productos": productos})