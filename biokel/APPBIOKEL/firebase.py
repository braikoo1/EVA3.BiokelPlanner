import firebase_admin
from firebase_admin import credentials, firestore
import os

firebase_key_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'biokel-firebase-key.json'
)

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
def sumar_inventario(tipo, cantidad, unidad):
    coleccion = db.collection("inventario")
    query = coleccion.where("tipo", "==", tipo).limit(1).get()

    if query:
        doc = query[0]
        datos = doc.to_dict()
        nueva_cantidad = datos["cantidad"] + cantidad
        coleccion.document(doc.id).update({"cantidad": nueva_cantidad})
    else:
        coleccion.add({
            "tipo": tipo,
            "cantidad": cantidad,
            "unidad": unidad
        })