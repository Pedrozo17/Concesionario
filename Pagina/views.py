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

            db.collection('perfiles').document(user.uid).set({
                'email': email,
                'uid': user.uid,
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"
            return redirect('login')
        except Exception as e:
            mensaje = f"☢️Error: {e}"
    return render(request, 'registro.html', {'mensaje': mensaje})

    #Logica para inicio de sesion
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwards):
        if 'uid' not in request.session:
            messages.warning(request, "☢️Warning, no has iniciado sesión.")
            return redirect('login')
        return view_func(request, *args, **kwards)
    return _wrapped_view

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

def cerrar_sesion(request):
#Limpiar la sesion y luego se redirije
    request.session.flush()
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login.html')