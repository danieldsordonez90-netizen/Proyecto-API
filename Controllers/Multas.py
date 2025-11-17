import json
import logging
from typing import List
from fastapi import HTTPException
from datetime import date 

from Models.Multas import Multa
from utils.database import execute_query_json
# Importamos obtener_prestamo para validar la existencia
from Controllers.Prestamos import obtener_prestamo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función interna para obtener una multa por su ID.
async def obtener_multa(id_multa: int) -> Multa:
    sqlfind = """
        SELECT 
            M.[Id_multa], M.[Id_prestamo], M.[Fecha_multa], M.[Monto],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[multa] AS M
        LEFT JOIN [biblioteca].[prestamo] AS P ON M.Id_prestamo = P.Id_prestamo
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        WHERE M.[Id_multa] = ?;
    """
    params = [id_multa]
    try:
        result = await execute_query_json(sqlfind, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                multa_data = result_dict[0]
                if multa_data.get('Fecha_multa'):
                    multa_data['Fecha_multa'] = date.fromisoformat(multa_data['Fecha_multa'])
                return multa_data
        
        raise HTTPException(status_code=404, detail=f"Multa con ID {id_multa} no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 1. Obtiene la multa asociada a un préstamo.
async def obtener_multa_de_prestamo(id_prestamo: int) -> Multa:
    sqlfind = """
        SELECT 
            M.[Id_multa], M.[Id_prestamo], M.[Fecha_multa], M.[Monto],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[multa] AS M
        LEFT JOIN [biblioteca].[prestamo] AS P ON M.Id_prestamo = P.Id_prestamo
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        WHERE M.[Id_prestamo] = ?;
    """
    params = [id_prestamo]
    try:
        result = await execute_query_json(sqlfind, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                multa_data = result_dict[0]
                if multa_data.get('Fecha_multa'):
                    multa_data['Fecha_multa'] = date.fromisoformat(multa_data['Fecha_multa'])
                return multa_data
        
        raise HTTPException(status_code=404, detail=f"El préstamo {id_prestamo} no tiene una multa asociada")
    except HTTPException as e:
        if e.status_code == 404:
            raise e
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 2. Obtiene todas las multas de la base de datos.
async def obtener_todas_multas() -> List[Multa]:
    sqlscript = """
        SELECT 
            M.[Id_multa], M.[Id_prestamo], M.[Fecha_multa], M.[Monto],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[multa] AS M
        LEFT JOIN [biblioteca].[prestamo] AS P ON M.Id_prestamo = P.Id_prestamo
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        ORDER BY M.Fecha_multa DESC;
    """
    try:
        result = await execute_query_json(sqlscript)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 3. Crea una nueva multa manualmente en la base de datos.
async def crear_multa_manual(multa: Multa) -> Multa:
    
    # Regla 2.1: Un préstamo solo puede tener UNA multa
    try:
        multa_existente = await obtener_multa_de_prestamo(multa.Id_prestamo)
        if multa_existente:
            raise HTTPException(status_code=409, detail="Conflicto: Este préstamo ya tiene una multa asociada")
    except HTTPException as e:
        if e.status_code != 404: # 404 es bueno (no hay multa)
            raise e
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error verificando multa: {str(e)}")

    # Verificamos que el préstamo al que se asocia la multa exista
    try:
        await obtener_prestamo(multa.Id_prestamo)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"El Préstamo con ID {multa.Id_prestamo} no existe")
        raise e

    sqlscript = """
        INSERT INTO [biblioteca].[multa] ([Id_prestamo], [Fecha_multa], [Monto])
        OUTPUT INSERTED.Id_multa AS NuevoId
        VALUES (?, GETDATE(), ?);
    """
    params = [multa.Id_prestamo, multa.Monto]

    try:
        result = await execute_query_json(sqlscript, params, needs_commit=True)
        if result:
            nuevo_id = json.loads(result)[0]['NuevoId']
            return await obtener_multa(nuevo_id) # Devuelve la versión "rica"
        
        raise HTTPException(status_code=500, detail="No se pudo crear la multa")
    except Exception as e:
        # Este error es ahora redundante porque ya lo validamos arriba, pero es buena práctica
        if "FOREIGN KEY" in str(e) and "prestamo" in str(e):
            raise HTTPException(status_code=404, detail=f"El Préstamo con ID {multa.Id_prestamo} no existe")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")