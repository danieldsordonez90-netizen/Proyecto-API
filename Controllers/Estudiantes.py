import json
import logging
from typing import List
from fastapi import HTTPException

from Models.Estudiantes import Estudiante
from utils.database import execute_query_json
from Controllers.Prestamos import contar_prestamos_activos 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtiene un estudiante específico por su ID.
async def obtener_estudiante(id: int) -> Estudiante:
    selectscript = """
        SELECT [id_matricula_estudiante], [Nombre_estudiante], 
               [Correo_estudiante], [Edad], [Esta_Activo]
        FROM [biblioteca].[estudiante]
        WHERE [id_matricula_estudiante] = ?
    """
    params = [id]
    try:
        result = await execute_query_json(selectscript, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                return result_dict[0]
        raise HTTPException(status_code=404, detail=f"Estudiante con id {id} no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Obtiene una lista de todos los estudiantes que están activos.
async def obtener_todos_estudiantes() -> List[Estudiante]:
    selectscript = """
        SELECT [id_matricula_estudiante], [Nombre_estudiante], 
               [Correo_estudiante], [Edad], [Esta_Activo]
        FROM [biblioteca].[estudiante]
        WHERE [Esta_Activo] = 1;
    """
    try:
        result = await execute_query_json(selectscript)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Registra un nuevo estudiante en la base de datos.
async def crear_estudiante(estudiante: Estudiante) -> Estudiante:
    sqlscript: str = """
        INSERT INTO [biblioteca].[estudiante] ([Nombre_estudiante], [Correo_estudiante], [Edad])
        OUTPUT INSERTED.id_matricula_estudiante AS NuevoId
        VALUES (?, ?, ?);
    """
    params = [
        estudiante.Nombre_estudiante,
        estudiante.Correo_estudiante,
        estudiante.Edad
    ]
    try:
        result = await execute_query_json(sqlscript, params, needs_commit=True)
        if result:
            nuevo_id = json.loads(result)[0]['NuevoId']
            return await obtener_estudiante(nuevo_id)
        raise HTTPException(status_code=500, detail="No se pudo crear el estudiante")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Actualiza los datos de un estudiante (incluyendo estado Activo/Inactivo).
async def actualizar_estudiante(estudiante: Estudiante) -> Estudiante:
    id_estudiante = estudiante.id_matricula_estudiante
    if id_estudiante is None:
        raise HTTPException(status_code=400, detail="El id_matricula_estudiante es necesario para actualizar.")

    # Regla de negocio: Si se intenta desactivar, validar préstamos pendientes.
    if estudiante.Esta_Activo is False:
        activos = await contar_prestamos_activos(id_estudiante)
        if activos > 0:
            raise HTTPException(status_code=409, 
                detail=f"Conflicto: No se puede desactivar. El estudiante tiene {activos} préstamos activos.")

    # Prepara el update dinámico excluyendo campos nulos y el ID.
    datos_dict = estudiante.model_dump(exclude={'id_matricula_estudiante'}, exclude_none=True) 

    if not datos_dict:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")

    llaves = [k for k in datos_dict.keys()]
    variables = " = ?, ".join(llaves) + " = ?"

    updatescript = f"""
        UPDATE [biblioteca].[estudiante]
        SET {variables}
        WHERE [id_matricula_estudiante] = ?;
    """
    params = [datos_dict[k] for k in llaves]
    params.append(id_estudiante)

    try:
        await obtener_estudiante(id_estudiante) # Asegura que existe
        await execute_query_json(updatescript, params, needs_commit=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando estudiante: {str(e)}")

    return await obtener_estudiante(id_estudiante)