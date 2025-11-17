from typing import List
from fastapi import APIRouter, HTTPException, status

from Models.Autores import Autor
from Models.Libros import Libro 

from Controllers.Autores import (
    crear_autor,
    obtener_autor,
    obtener_todos_autores,
    actualizar_autor,
    obtener_libros_de_autor 
)

router = APIRouter(prefix="/autores")

# --- GET (Listar todos) ---
@router.get("/", tags=["Autores"], response_model=List[Autor], status_code=status.HTTP_200_OK)
async def listar_autores():
    return await obtener_todos_autores()

# --- GET /{id} (Buscar uno) ---
@router.get("/{id}", tags=["Autores"], response_model=Autor, status_code=status.HTTP_200_OK)
async def buscar_autor(id: int):
    return await obtener_autor(id)

# --- POST (Crear) ---
@router.post("/", tags=["Autores"], response_model=Autor, status_code=status.HTTP_201_CREATED)
async def registrar_autor(autor: Autor):
    return await crear_autor(autor)

# --- PUT /{id} (Actualizar) ---
@router.put("/{id}", tags=["Autores"], response_model=Autor, status_code=status.HTTP_200_OK)
async def actualizar_datos_autor(id: int, autor: Autor):
    autor.Id_autor = id
    return await actualizar_autor(autor)

# --- ENDPOINT DE RELACIÓN (Autor -> Libros) ---
@router.get("/{id}/libros", tags=["Autores (Relaciones)"], response_model=List[Libro])
async def ver_libros_del_autor(id: int):
    """Obtiene la lista de libros ("respuesta rica") de un autor específico."""
    return await obtener_libros_de_autor(id)