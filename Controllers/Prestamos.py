# Archivo: Controllers/Prestamos.py

import json
import logging
from typing import List
from fastapi import HTTPException
from datetime import date 

from Models.Prestamos import Prestamo
from utils.database import execute_query_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función interna para obtener un préstamo por su ID.
async def obtener_prestamo(id_prestamo: int) -> Prestamo:
    sqlfind = """
        SELECT 
            P.[Id_prestamo], P.[Id_matricula_estudiante], P.[ISBN], 
            P.[Fecha_prestamo], P.[Fecha_devolucion],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[prestamo] AS P
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        WHERE P.[Id_prestamo] = ?;
    """
    params = [id_prestamo]
    try:
        result = await execute_query_json(sqlfind, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                prestamo_data = result_dict[0]
                if prestamo_data.get('Fecha_prestamo'):
                    prestamo_data['Fecha_prestamo'] = date.fromisoformat(prestamo_data['Fecha_prestamo'])
                if prestamo_data.get('Fecha_devolucion'):
                    prestamo_data['Fecha_devolucion'] = date.fromisoformat(prestamo_data['Fecha_devolucion'])
                return prestamo_data
        
        raise HTTPException(status_code=404, detail=f"Préstamo con ID {id_prestamo} no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# Función interna para contar los préstamos activos de un estudiante.
async def contar_prestamos_activos(id_estudiante: int) -> int:
    sqlcount = """
        SELECT COUNT(Id_prestamo) as total_activos
        FROM [biblioteca].[prestamo]
        WHERE [Id_matricula_estudiante] = ? AND [Fecha_devolucion] IS NULL;
    """
    params = [id_estudiante]
    try:
        result = await execute_query_json(sqlcount, params=params)
        if result:
            result_dict = json.loads(result)
            return result_dict[0]['total_activos']
        return 0
    except Exception as e:
        logger.error(f"Error contando préstamos: {e}")
        return 99 

# 1. Crea un nuevo préstamo en la base de datos.
async def crear_prestamo(prestamo: Prestamo) -> Prestamo:
    
    activos = await contar_prestamos_activos(prestamo.Id_matricula_estudiante)
    if activos >= 5:
        raise HTTPException(status_code=400, detail="Límite de 5 préstamos activos alcanzado")
    
    sqlscript = """
        INSERT INTO [biblioteca].[prestamo] 
            ([Id_matricula_estudiante], [ISBN], [Fecha_prestamo], [Fecha_devolucion])
        OUTPUT INSERTED.Id_prestamo AS NuevoId
        VALUES (?, ?, GETDATE(), NULL);
    """
    
    params = [prestamo.Id_matricula_estudiante, prestamo.ISBN]

    try:
        result = await execute_query_json(sqlscript, params, needs_commit=True)
        if result:
            result_dict = json.loads(result)
            nuevo_id = result_dict[0]['NuevoId'] 
            return await obtener_prestamo(nuevo_id) # Devuelve la versión "rica"
        
        raise HTTPException(status_code=500, detail="No se pudo crear el préstamo")
    except Exception as e:
        logger.error(f"Error creando préstamo: {e}")
        if "FOREIGN KEY" in str(e) and "estudiante" in str(e):
            raise HTTPException(status_code=404, detail=f"El Estudiante con ID {prestamo.Id_matricula_estudiante} no existe")
        if "FOREIGN KEY" in str(e) and "libro" in str(e):
            raise HTTPException(status_code=404, detail=f"El Libro con ISBN {prestamo.ISBN} no existe")
        
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 2. Registra la devolución de un préstamo.
async def registrar_devolucion(id_prestamo: int, fecha_devolucion: date) -> Prestamo:
    
    prestamo_actual = await obtener_prestamo(id_prestamo)
    if prestamo_actual['Fecha_devolucion'] is not None:
        raise HTTPException(status_code=400, detail="Este préstamo ya fue devuelto")

    sql_prestamo = """
        UPDATE [biblioteca].[prestamo]
        SET [Fecha_devolucion] = ?
        WHERE [Id_prestamo] = ?;
    """
    params_prestamo = [fecha_devolucion, id_prestamo]

    try:
        await execute_query_json(sql_prestamo, params_prestamo, needs_commit=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando préstamo: {str(e)}")

    return await obtener_prestamo(id_prestamo) # Devuelve la versión "rica"

# 3. Obtiene todos los préstamos de la base de datos.
async def obtener_todos_prestamos() -> List[Prestamo]:
    sqlscript = """
        SELECT 
            P.[Id_prestamo], P.[Id_matricula_estudiante], P.[ISBN], 
            P.[Fecha_prestamo], P.[Fecha_devolucion],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[prestamo] AS P
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        ORDER BY P.Fecha_prestamo DESC;
    """
    try:
        result = await execute_query_json(sqlscript)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 4. Obtiene todos los préstamos de un estudiante específico.
async def obtener_prestamos_de_estudiante(id_estudiante: int) -> List[Prestamo]:
    sqlscript = """
        SELECT 
            P.[Id_prestamo], P.[Id_matricula_estudiante], P.[ISBN], 
            P.[Fecha_prestamo], P.[Fecha_devolucion],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[prestamo] AS P
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        WHERE P.[id_matricula_estudiante] = ?
        ORDER BY P.Fecha_prestamo DESC;
    """
    params = [id_estudiante]
    try:
        result = await execute_query_json(sqlscript, params=params)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 5. Obtiene todos los préstamos de un libro específico.
async def obtener_prestamos_de_libro(isbn: str) -> List[Prestamo]:
    sqlscript = """
        SELECT 
            P.[Id_prestamo], P.[Id_matricula_estudiante], P.[ISBN], 
            P.[Fecha_prestamo], P.[Fecha_devolucion],
            E.Nombre_estudiante,
            L.Titulo
        FROM [biblioteca].[prestamo] AS P
        LEFT JOIN [biblioteca].[estudiante] AS E ON P.id_matricula_estudiante = E.id_matricula_estudiante
        LEFT JOIN [biblioteca].[libro] AS L ON P.ISBN = L.ISBN
        WHERE P.[ISBN] = ?
        ORDER BY P.Fecha_prestamo DESC;
    """
    params = [isbn]
    try:
        result = await execute_query_json(sqlscript, params=params)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")