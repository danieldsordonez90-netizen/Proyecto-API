# Archivo: Routes/Estudiantes.py

from typing import List
from fastapi import APIRouter, HTTPException, status 

from Models.Estudiantes import Estudiante
from Models.Prestamos import Prestamo 
from Controllers.Estudiantes import (
    crear_estudiante,
    obtener_estudiante,
    obtener_todos_estudiantes,
    actualizar_estudiante,
    desactivar_estudiante
)
from Controllers.Prestamos import obtener_prestamos_de_estudiante

router = APIRouter(prefix="/estudiantes")

# --- Endpoints CRUD Básicos ---

@router.get("/", tags=["Estudiantes"], response_model=List[Estudiante], status_code=status.HTTP_200_OK)
async def listar_estudiantes():
    """Obtiene una lista de todos los estudiantes ACTIVOS."""
    return await obtener_todos_estudiantes()

@router.get("/{id}", tags=["Estudiantes"], response_model=Estudiante, status_code=status.HTTP_200_OK)
async def buscar_estudiante(id: int):
    """Busca un estudiante específico por su ID (activo o inactivo)."""
    return await obtener_estudiante(id)

@router.post("/", tags=["Estudiantes"], response_model=Estudiante, status_code=status.HTTP_201_CREATED)
async def registrar_estudiante(estudiante: Estudiante):
    return await crear_estudiante(estudiante)

@router.put("/{id}", tags=["Estudiantes"], response_model=Estudiante, status_code=status.HTTP_200_OK)
async def actualizar_datos_estudiante(id: int, estudiante: Estudiante):
    estudiante.id_matricula_estudiante = id
    return await actualizar_estudiante(estudiante)

@router.put("/{id}/desactivar", tags=["Estudiantes"])
async def desactivar_un_estudiante(id: int):
    """
    Desactiva un estudiante (Lo "alimina").
    Solo funciona si el estudiante no tiene préstamos activos.
    """
    return await desactivar_estudiante(id)

# --- Endpoints de Relaciones ---

@router.get("/{id}/prestamos", tags=["Estudiantes (Relaciones)"], response_model=List[Prestamo])
async def ver_prestamos_del_estudiante(id: int):
    """Obtiene la lista de todos los préstamos de un estudiante específico."""
    return await obtener_prestamos_de_estudiante(id)