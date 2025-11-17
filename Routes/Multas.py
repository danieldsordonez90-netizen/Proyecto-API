from typing import List
from fastapi import APIRouter, HTTPException, status

from Models.Multas import Multa
from Controllers.Multas import (
    obtener_multa,
    obtener_todas_multas,
    crear_multa_manual,
    obtener_multa_de_prestamo
)

router = APIRouter(prefix="/multas")

# --- GET (Listar todas) ---
@router.get("/", tags=["Multas"], response_model=List[Multa], status_code=status.HTTP_200_OK)
async def listar_multas():
    """Obtiene una lista de todas las multas registradas."""
    return await obtener_todas_multas()

# --- GET /{id} (Buscar una) ---
@router.get("/{id}", tags=["Multas"], response_model=Multa, status_code=status.HTTP_200_OK)
async def buscar_multa(id: int):
    """Busca una multa específica por su ID de Multa."""
    return await obtener_multa(id)

# --- POST (Crear manual) ---
@router.post("/", tags=["Multas"], response_model=Multa, status_code=status.HTTP_201_CREATED)
async def registrar_multa_manual(multa: Multa):
    """
    Registra una multa manualmente (ej. por daños, retraso manual).
    Payload esperado: { "Id_prestamo": int, "Monto": float }
    """
    return await crear_multa_manual(multa)

# --- Endpoint de Relación ---
@router.get("/prestamo/{id_prestamo}", tags=["Multas (Relaciones)"], response_model=Multa)
async def ver_multa_del_prestamo(id_prestamo: int):
    """Revisa si un préstamo tiene una multa asociada."""
    return await obtener_multa_de_prestamo(id_prestamo)