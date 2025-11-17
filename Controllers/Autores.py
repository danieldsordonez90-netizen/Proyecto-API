import json
import logging
from typing import List
from fastapi import HTTPException

from Models.Autores import Autor
from Models.Libros import Libro
from utils.database import execute_query_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Obtiene un autor específico por su ID.
async def obtener_autor(id: int) -> Autor:
    selectscript = """
        SELECT [Id_autor], [Nombre_autor], [Año_nacimiento]
        FROM [biblioteca].[autor]
        WHERE [Id_autor] = ?
    """
    params = [id]
    try:
        result = await execute_query_json(selectscript, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                return result_dict[0]
        raise HTTPException(status_code=404, detail=f"Autor con id {id} no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 2. Obtiene la lista completa de autores.
async def obtener_todos_autores() -> List[Autor]:
    selectscript = """
        SELECT [Id_autor], [Nombre_autor], [Año_nacimiento]
        FROM [biblioteca].[autor]
    """
    try:
        result = await execute_query_json(selectscript)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 3. Crea un nuevo autor en la base de datos.
async def crear_autor(autor: Autor) -> Autor:
    sqlscript = "INSERT INTO [biblioteca].[autor] ([Nombre_autor], [Año_nacimiento]) VALUES (?, ?);"
    params = [autor.Nombre_autor, autor.Año_nacimiento]
    try:
        await execute_query_json(sqlscript, params, needs_commit=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando autor: {str(e)}")

    sqlfind = "SELECT TOP 1 [Id_autor] FROM [biblioteca].[autor] ORDER BY [Id_autor] DESC"
    try:
        result_find = await execute_query_json(sqlfind)
        if result_find:
            nuevo_id = json.loads(result_find)[0]['Id_autor']
            return await obtener_autor(nuevo_id)
        raise HTTPException(status_code=500, detail="No se pudo recuperar el autor creado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando autor creado: {str(e)}")

# 4. Actualiza los datos de un autor existente.
async def actualizar_autor(autor: Autor) -> Autor:
    if autor.Id_autor is None:
        raise HTTPException(status_code=400, detail="El Id_autor es necesario para actualizar.")
    datos_dict = autor.model_dump(exclude={'Id_autor'}, exclude_none=True)
    if not datos_dict:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
    llaves = [k for k in datos_dict.keys()]
    variables = " = ?, ".join(llaves) + " = ?"
    updatescript = f"UPDATE [biblioteca].[autor] SET {variables} WHERE [Id_autor] = ?;"
    params = [datos_dict[k] for k in llaves]
    params.append(autor.Id_autor)
    try:
        await execute_query_json(updatescript, params, needs_commit=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando autor: {str(e)}")
    return await obtener_autor(autor.Id_autor)

# 5. Obtiene la lista de libros escritos por un autor específico.
async def obtener_libros_de_autor(id_autor: int) -> List[Libro]:

    # Primero verificamos si el autor existe para dar un error 404 claro.
    await obtener_autor(id_autor)

    # Consulta para obtener los libros del autor.
    sqlscript = """
        SELECT
            L.[ISBN], L.[Titulo], L.[Año_publicacion]
        FROM [biblioteca].[libro] AS L
        INNER JOIN [biblioteca].[libro_autor] AS LA
            ON L.[ISBN] = LA.[ISBN]
        WHERE LA.[Id_autor] = ?;
    """
    params = [id_autor]

    try:
        result = await execute_query_json(sqlscript, params=params)
        if result:
            return json.loads(result)
        # Si el autor existe pero no tiene libros, devuelve una lista vacía.
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")