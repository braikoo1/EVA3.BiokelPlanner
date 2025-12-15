from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .firebase import get_db
from django.http import HttpResponse
import json
from collections import defaultdict
from .forms import InventarioForm
from datetime import datetime


def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("inicio")
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

        if not username or not password:
            mensaje = "Debes ingresar usuario y contraseña"
        elif User.objects.filter(username=username).exists():
            mensaje = "Ese usuario ya existe"
        else:
            User.objects.create_user(username=username, password=password)
            return redirect("login")

    return render(request, "registrarse.html", {"mensaje": mensaje})


@login_required
def raciones(request):
    resultados = None

    if request.method == "POST":
        gallinas = int(request.POST.get("gallinas"))
        algas = float(request.POST.get("algas"))
        calcio = float(request.POST.get("calcio"))
        alimento = float(request.POST.get("alimento"))

        # consumo diario
        algas_dia = algas * gallinas
        calcio_dia = calcio * gallinas
        alimento_dia = alimento * gallinas

        mezcla_dia = algas_dia + calcio_dia + alimento_dia

        # semanal
        algas_sem = algas_dia * 7
        calcio_sem = calcio_dia * 7
        alimento_sem = alimento_dia * 7
        mezcla_sem = mezcla_dia * 7
        mezcla_sem_opt = mezcla_sem * 0.85

        # mensual
        algas_mes = algas_dia * 30
        calcio_mes = calcio_dia * 30
        alimento_mes = alimento_dia * 30
        mezcla_mes = mezcla_dia * 30
        mezcla_mes_opt = mezcla_mes * 0.85

        resultados = {
            "gallinas": gallinas,

            "algas_sem": algas_sem,
            "calcio_sem": calcio_sem,
            "alimento_sem": alimento_sem,
            "mezcla_sem": round(mezcla_sem / 1000, 2),
            "mezcla_sem_opt": round(mezcla_sem_opt / 1000, 2),

            "algas_mes": algas_mes,
            "calcio_mes": calcio_mes,
            "alimento_mes": alimento_mes,
            "mezcla_mes": round(mezcla_mes / 1000, 2),
            "mezcla_mes_opt": round(mezcla_mes_opt / 1000, 2),
        }

    return render(request, "raciones.html", {"resultados": resultados})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def inventario(request):
    db = get_db()
    inventario_ref = db.collection("inventario")

    form = InventarioForm(request.POST or None)
    item_editar = None

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        tipo = request.POST.get("tipo")
        cantidad_input = float(request.POST.get("cantidad", 0))
        accion = request.POST.get("accion") 

        if not tipo:
            return redirect("inventario")

        docs = inventario_ref.where("tipo", "==", tipo).stream()
        existente = None
        cantidad_actual = 0
        for d in docs:
            existente = d
            cantidad_actual = d.to_dict().get("cantidad", 0)
            break

        if accion == "editar":
            cantidad_nueva = cantidad_input
        elif accion == "agregar":
            cantidad_nueva = cantidad_actual + cantidad_input
        elif accion == "restar":
            cantidad_nueva = max(cantidad_actual - cantidad_input, 0)
        else:
            cantidad_nueva = cantidad_actual

        if existente:
            inventario_ref.document(existente.id).update({"cantidad": cantidad_nueva})
        else:
            inventario_ref.add({
                "tipo": tipo,
                "cantidad": cantidad_nueva,
                "unidad": "kg"
            })

        db.collection("historial_inventario").add({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": request.user.username,
            "tipo": tipo,
            "cantidad": f"{cantidad_actual} -> {cantidad_nueva}",
            "accion": accion.capitalize()
        })

        return redirect("inventario")

    inventario = []
    for doc in inventario_ref.stream():
        item = doc.to_dict()
        item["id"] = doc.id
        inventario.append(item)

    return render(request, "inventario.html", {
        "form": form,
        "inventario": inventario,
        "item_editar": item_editar
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reportes(request):
    db = get_db()
    historial_ref = db.collection("historial_inventario")

    historial = []
    for doc in historial_ref.order_by("fecha", direction="DESCENDING").stream():
        data = doc.to_dict()
        historial.append(data)

    return render(request, "reportes.html", {
        "historial": historial
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def huevos(request):
    db = get_db()
    huevos_ref = db.collection("produccion_huevos")
    inventario_ref = db.collection("inventario")

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        cantidad = request.POST.get("cantidad")

        if fecha and cantidad:
            cantidad = int(cantidad)

            huevos_ref.add({
                "fecha": fecha,
                "cantidad": cantidad
            })

            docs = inventario_ref.where("tipo", "==", "huevos").stream()
            encontrado = False

            for doc in docs:
                data = doc.to_dict()
                inventario_ref.document(doc.id).update({
                    "cantidad": data["cantidad"] + cantidad
                })
                encontrado = True
                break

            if not encontrado:
                inventario_ref.add({
                    "tipo": "huevos",
                    "cantidad": cantidad,
                    "unidad": "u"
                })

    registros = []
    for doc in huevos_ref.stream():
        registros.append(doc.to_dict())

    return render(request, "huevos.html", {
        "registros": registros
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def metricas(request):
    db = get_db()

    huevos_ref = db.collection("produccion_huevos")
    produccion_huevos = defaultdict(int)
    for doc in huevos_ref.stream():
        data = doc.to_dict()
        fecha = data.get("fecha")
        cantidad = data.get("cantidad", 0)
        if fecha:
            produccion_huevos[fecha] += cantidad

    fechas_huevos = sorted(produccion_huevos.keys())
    valores_huevos = [produccion_huevos[f] for f in fechas_huevos]

    historial_ref = db.collection("historial_inventario")
    stock_algas = defaultdict(float)
    stock_calcio = defaultdict(float)
    inventario_actual = {"algas": 0, "calcio": 0}

    for doc in historial_ref.stream():
        data = doc.to_dict()
        tipo = data.get("tipo")
        cantidad_str = data.get("cantidad", "0")
        accion = data.get("accion", "")
        fecha = data.get("fecha", "Actual")

        if "->" in cantidad_str:
            antes, despues = cantidad_str.split("->")
            cantidad_final = float(despues.strip())
        else:
            cantidad_final = float(cantidad_str.strip() or 0)

        if tipo == "algas":
            stock_algas[fecha] = cantidad_final
            inventario_actual["algas"] = cantidad_final
        elif tipo == "calcio":
            stock_calcio[fecha] = cantidad_final
            inventario_actual["calcio"] = cantidad_final

    fechas_algas = sorted(stock_algas.keys())
    valores_algas = [stock_algas[f] for f in fechas_algas]

    fechas_calcio = sorted(stock_calcio.keys())
    valores_calcio = [stock_calcio[f] for f in fechas_calcio]

    return render(request, "metricas.html", {
        "fechas_huevos": json.dumps(fechas_huevos),
        "valores_huevos": json.dumps(valores_huevos),
        "fechas_algas": json.dumps(fechas_algas),
        "valores_algas": json.dumps(valores_algas),
        "fechas_calcio": json.dumps(fechas_calcio),
        "valores_calcio": json.dumps(valores_calcio),
    })
