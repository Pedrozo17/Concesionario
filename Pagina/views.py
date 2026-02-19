from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
from config.firebase_connection import initialize_firebase
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

db = initialize_firebase()

'''

def login_required_firebase(view_func):
    """
    Decorador que verifica si el usuario inició sesión usando Firebase.
    Si no existe 'uid' en la sesión, lo redirige al login.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if 'uid' not in request.session:
            messages.warning(request, "Debes iniciar sesión primero.")
            return redirect('login')   # cambia 'login' si tu url se llama distinto

        return view_func(request, *args, **kwargs)

    return _wrapped_view
'''

def dashboard(request):
    return render(request, 'dashboard.html')


# @login_required_firebase
def crear_carro(request):
    if request.method == 'POST':
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        precio = request.POST.get('precio')

        db.collection('carros').add({
            'marca': marca,
            'modelo': modelo,
            'precio': precio,
            'fecha': firestore.SERVER_TIMESTAMP
        })

        messages.success(request, "Carro creado correctamente")
        return redirect('dashboard')

    return render(request, 'carros/crear.html')


# @login_required_firebase
def ver_carro(request, carro_id):
    doc = db.collection('carros').document(carro_id).get()

    if not doc.exists:
        messages.error(request, "Carro no existe")
        return redirect('dashboard')

    carro = doc.to_dict()
    carro['id'] = doc.id

    return render(request, 'carros/ver.html', {'carro': carro})


# @login_required_firebase
def editar_carro(request, carro_id):
    ref = db.collection('carros').document(carro_id)
    doc = ref.get()

    if not doc.exists:
        messages.error(request, "Carro no existe")
        return redirect('dashboard')

    carro = doc.to_dict()
    carro['id'] = doc.id

    if request.method == 'POST':
        ref.update({
            'marca': request.POST.get('marca'),
            'modelo': request.POST.get('modelo'),
            'precio': request.POST.get('precio'),
        })
        messages.success(request, "Carro actualizado")
        return redirect('ver_carro', carro_id=carro_id)

    return render(request, 'carros/editar.html', {'carro': carro})


# @login_required_firebase
def eliminar_carro(request, carro_id):
    db.collection('carros').document(carro_id).delete()
    messages.success(request, "Carro eliminado")
    return redirect('dashboard')
