import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    try:
        if not firebase_admin._apps:

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            file_name = os.getenv("FIREBASE_KEYS_PATH")

            if not file_name:
                raise ValueError("FIREBASE_KEYS_PATH no está definida")

            cert_path = os.path.join(project_root, file_name)

            if not os.path.exists(cert_path):
                raise FileNotFoundError(f"No se encontró el archivo en {cert_path}")

            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)

            print("🔥 Firebase inicializado correctamente")

        return firestore.client()

    except Exception as e:
        print("❌ Error al inicializar Firebase:", e)
        return None