# Importaciones necesarias de FastAPI y los routers de cada módulo.
from typing import Union
from fastapi import FastAPI
from Routes.Estudiantes import router as router_estudiantes
from Routes.Autores import router as router_autores
from Routes.Libros import router as router_libros
from Routes.Prestamos import router as router_prestamos
from Routes.Multas import router as router_multas

# Creación de la instancia de la aplicación FastAPI con título, descripción y versión.
app = FastAPI(
    title="API de Biblioteca",
    description="API para gestionar la tabla de estudiantes.",
    version="1.0.0"
)

# Inclusión de los routers para cada recurso de la API.
app.include_router(router_estudiantes)
app.include_router(router_autores)
app.include_router(router_libros)
app.include_router(router_prestamos)
app.include_router(router_multas)

# Definición de la ruta raíz que devuelve un mensaje de bienvenida.
@app.get("/")
def read_root():
    """
    Ruta raíz que devuelve un mensaje indicando que la API está funcionando.
    """
    return {"API": "Biblioteca de Estudiantes - Funcionando Correctamente"}

# Ruta de ejemplo para leer un item con un ID y un parámetro opcional.
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    """
    Ruta de ejemplo para demostrar el paso de parámetros en la URL y query params.
    """
    return {"item_id": item_id, "q": q}