from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
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

@login_required
def raciones(request):
    return render(request, "raciones.html")

@login_required
def huevos(request):
    return render(request, "huevos.html")

@login_required
def reportes(request):
    return render(request, "reportes.html")

@login_required
def inventario(request):
    return render(request, "inventario.html")
