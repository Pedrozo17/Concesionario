from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from config.firebase_connection import initialize_firebase
from functools import wraps 
import requests
import os
# Create your views here.

db = initialize_firebase()





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

db = initialize_firebase()

@login_required_firebase
def dashboard(request):
    carros_ref = db.collection('carros')
    docs = carros_ref.stream()

    carros = []

    for doc in docs:
        carro = doc.to_dict()
        carro['id'] = doc.id  # importante para usar carro.id en el template
        carros.append(carro)

    context = {
        'carros': carros
    }

    return render(request, 'dashboard.html', context)



@login_required_firebase
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


@login_required_firebase
def ver_carro(request, carro_id):
    doc = db.collection('carros').document(carro_id).get()

    if not doc.exists:
        messages.error(request, "Carro no existe")
        return redirect('dashboard')

    carro = doc.to_dict()
    carro['id'] = doc.id

    return render(request, 'carros/ver.html', {'carro': carro})


@login_required_firebase
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


@login_required_firebase
def eliminar_carro(request, carro_id):
    db.collection('carros').document(carro_id).delete()
    messages.success(request, "Carro eliminado")
    return redirect('dashboard')


def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Vamos a crear en Firebase auth
            user = auth.create_user(
                email = email,
                password = password
            )

            #CREAR EN FIRESTORE

            db.collection('usuarios').document(user.uid).set({
                'email': email,
                'uid': user.uid,
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"
            return redirect('login')
        except Exception as e:
            mensaje = f"☢️Error: {e}"
    return render(request, 'registro.html', {'mensaje': mensaje})

def iniciar_sesion(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_API_KEY')
        #Endpoint oficial de google
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200:
                #Todo fue bien
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['idToken'] = data['idToken']
                messages.success(request, f"✅Acceso correcto al sistema.")
                return redirect('dashboard')
            else:
                #Error: analizar el error
                error_message = data.get('error', {}).get('message', 'UNKNOWN_ERROR')

                errores_comunes = {
                     'INVALID_LOGIN_CREDENTIALS': 'La contraseña es incorrecta o el correo no es válido.',
                    'EMAIL_NOT_FOUND': 'Este correo no está registrado en el sistema.',
                    'USER_DISABLED': 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Demasiados intentos fallidos. Espere unos minutos.'
                }

                mensaje_usuario = errores_comunes.get(error_message, 'Error de autenticación, revisa tus credenciales.')
                messages.error(request, mensaje_usuario)
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con el servidor")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    return render(request, 'login.html')

@login_required_firebase
def cerrar_sesion(request):
#Limpiar la sesion y luego se redirije
    request.session.flush()
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login.html')