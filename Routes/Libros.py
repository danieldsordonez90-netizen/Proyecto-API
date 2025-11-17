from typing import List
from fastapi import APIRouter, HTTPException, status

from Models.Libros import Libro
from Models.Autores import Autor 
from Models.Prestamos import Prestamo 

from Controllers.Libros import (
    crear_libro,
    obtener_libro,
    obtener_todos_libros,
    actualizar_libro,
    eliminar_libro,
    
    asignar_autor_a_libro,
    obtener_autores_de_libro,
    quitar_autor_de_libro
)
from Controllers.Prestamos import obtener_prestamos_de_libro

router = APIRouter(prefix="/libros")

# CRUD BÁSICO DE LIBROS

# --- GET (Listar todos) ---
@router.get("/", tags=["Libros"], response_model=List[Libro], status_code=status.HTTP_200_OK)
async def listar_libros():
    """Obtiene una lista de todos los libros en el catálogo."""
    return await obtener_todos_libros()

# --- GET /{isbn} (Buscar uno) ---
@router.get("/{isbn}", tags=["Libros"], response_model=Libro, status_code=status.HTTP_200_OK)
async def buscar_libro(isbn: str):
    """Busca un libro específico por su ISBN."""
    return await obtener_libro(isbn)

# --- POST (Crear) ---
@router.post("/", tags=["Libros"], response_model=Libro, status_code=status.HTTP_201_CREATED)
async def registrar_libro(libro: Libro):
    """Registra un nuevo libro en el catálogo."""
    return await crear_libro(libro)

# --- PUT /{isbn} (Actualizar) ---
@router.put("/{isbn}", tags=["Libros"], response_model=Libro, status_code=status.HTTP_200_OK)
async def actualizar_datos_libro(isbn: str, libro: Libro):
    """Actualiza el Título o Año de un libro existente."""
    return await actualizar_libro(isbn, libro)

# --- DELETE /{isbn} (Eliminar) ---
@router.delete("/{isbn}", tags=["Libros"], status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_un_libro(isbn: str):
    """Elimina un libro del catálogo (si no tiene préstamos o autores asociados)."""
    await eliminar_libro(isbn)
    return None

# ENDPOINTS DE RELACIÓN (Libro <-> Autor)

# --- POST /libros/{isbn}/autores/{id_autor} (Asignar) ---
@router.post("/{isbn}/autores/{id_autor}", tags=["Libros (Relaciones)"], status_code=status.HTTP_201_CREATED)
async def asignar_autor(isbn: str, id_autor: int):
    """Asigna un autor existente a un libro existente."""
    return await asignar_autor_a_libro(isbn, id_autor)

# --- GET /libros/{isbn}/autores (Respuesta "Rica") ---
@router.get("/{isbn}/autores", tags=["Libros (Relaciones)"], response_model=List[Autor])
async def ver_autores_del_libro(isbn: str):
    """Obtiene la lista de autores de un libro específico."""
    return await obtener_autores_de_libro(isbn)

# --- DELETE /libros/{isbn}/autores/{id_autor} (Quitar) ---
@router.delete("/{isbn}/autores/{id_autor}", 
              tags=["Libros (Relaciones)"], 
              status_code=status.HTTP_200_OK) # <--- 1. Cambiado a 200 OK
async def quitar_autor(isbn: str, id_autor: int):
    """Quita la asignación de un autor a un libro."""
    # 2. Ahora retornamos el mensaje del controlador
    return await quitar_autor_de_libro(isbn, id_autor)

# ENDPOINT DE RELACIÓN 
@router.get("/{isbn}/prestamos", tags=["Libros (Relaciones)"], response_model=List[Prestamo])
async def ver_prestamos_del_libro(isbn: str):
    """Obtiene el historial de préstamos de un libro específico."""
    return await obtener_prestamos_de_libro(isbn)