from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field 
from datetime import date     

from Models.Prestamos import Prestamo
from Controllers.Prestamos import (
    crear_prestamo,
    obtener_prestamo,
    obtener_todos_prestamos,
    registrar_devolucion
)

router = APIRouter(prefix="/prestamos")

class PayloadDevolucion(BaseModel):
    Fecha_devolucion: date = Field(..., example="2025-11-20")


# --- GET (Listar todos) ---
@router.get("/", tags=["Préstamos"], response_model=List[Prestamo], status_code=status.HTTP_200_OK)
async def listar_prestamos():
    return await obtener_todos_prestamos()

# --- GET /{id} (Buscar uno) ---
@router.get("/{id}", tags=["Préstamos"], response_model=Prestamo, status_code=status.HTTP_200_OK)
async def buscar_prestamo(id: int):
    return await obtener_prestamo(id)

# --- POST (Crear) ---
@router.post("/", tags=["Préstamos"], response_model=Prestamo, status_code=status.HTTP_201_CREATED)
async def registrar_prestamo(prestamo: Prestamo):
    """
    Crea un nuevo préstamo.
    Payload esperado: { "Id_matricula_estudiante": int, "ISBN": str }
    """
    return await crear_prestamo(prestamo)

# --- PUT /{id}/devolucion (Devolución Manual) ---
@router.put("/{id}/devolucion", tags=["Préstamos"], response_model=Prestamo, status_code=status.HTTP_200_OK)
async def devolver_prestamo(id: int, payload: PayloadDevolucion):
    """
    Marca un préstamo como devuelto usando la fecha manual provista.
    Payload esperado: { "Fecha_devolucion": "YYYY-MM-DD" }
    """
    return await registrar_devolucion(id, payload.Fecha_devolucion)