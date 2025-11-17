import json
import logging
from typing import List
from fastapi import HTTPException

from Models.Libros import Libro
from Models.Autores import Autor
from utils.database import execute_query_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Obtiene un libro por su ISBN.
async def obtener_libro(isbn: str) -> Libro:
    selectscript = """
        SELECT [ISBN], [Titulo], [Año_publicacion]
        FROM [biblioteca].[libro]
        WHERE [ISBN] = ?
    """
    params = [isbn]
    try:
        result = await execute_query_json(selectscript, params=params)
        if result:
            result_dict = json.loads(result)
            if len(result_dict) > 0:
                return result_dict[0]
        raise HTTPException(status_code=404, detail=f"Libro con ISBN {isbn} no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 2. Obtiene todos los libros.
async def obtener_todos_libros() -> List[Libro]:
    selectscript = """
        SELECT [ISBN], [Titulo], [Año_publicacion]
        FROM [biblioteca].[libro]
    """
    try:
        result = await execute_query_json(selectscript)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# 3. Crea un nuevo libro.
async def crear_libro(libro: Libro) -> Libro:
    try:
        existente = await obtener_libro(libro.ISBN)
        if existente:
            raise HTTPException(status_code=400, detail=f"Ya existe un libro con el ISBN {libro.ISBN}")
    except HTTPException as e:
        if e.status_code != 404:
            raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando ISBN: {str(e)}")

    sqlscript: str = """
        INSERT INTO [biblioteca].[libro] ([ISBN], [Titulo], [Año_publicacion])
        VALUES (?, ?, ?);
    """
    params = [libro.ISBN, libro.Titulo, libro.Año_publicacion]
    try:
        await execute_query_json(sqlscript, params, needs_commit=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando libro: {str(e)}")
    return await obtener_libro(libro.ISBN)

# 4. Actualiza un libro existente.
async def actualizar_libro(isbn: str, libro: Libro) -> Libro:
    datos_dict = libro.model_dump(exclude={'ISBN'}, exclude_none=True)
    if not datos_dict:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
    llaves = [k for k in datos_dict.keys()]
    variables = " = ?, ".join(llaves) + " = ?"
    updatescript = f"""
        UPDATE [biblioteca].[libro]
        SET {variables}
        WHERE [ISBN] = ?;
    """
    params = [datos_dict[k] for k in llaves]
    params.append(isbn) 
    try:
        await obtener_libro(isbn) 
        await execute_query_json(updatescript, params, needs_commit=True)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Libro con ISBN {isbn} no encontrado")
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando libro: {str(e)}")
    return await obtener_libro(isbn)

# 5. Elimina un libro por su ISBN.
async def eliminar_libro(isbn: str) -> str:
    deletescript = "DELETE FROM [biblioteca].[libro] WHERE [ISBN] = ?;"
    params = [isbn]
    try:
        await obtener_libro(isbn) 
        await execute_query_json(deletescript, params, needs_commit=True)
        return "ELIMINADO CORRECTAMENTE"
    except HTTPException as e:
        if e.status_code == 404:
             raise HTTPException(status_code=404, detail=f"Libro no encontrado")
        raise e
    except Exception as e:
        logger.error(f"Error de FK al eliminar libro: {e}")
        raise HTTPException(status_code=409, detail=f"No se puede eliminar: Conflicto de FK.")

# Asigna un autor a un libro.
async def asignar_autor_a_libro(isbn: str, id_autor: int):
    sqlscript = "INSERT INTO [biblioteca].[libro_autor] ([ISBN], [Id_autor]) VALUES (?, ?);"
    params = [isbn, id_autor]
    try:
        await obtener_libro(isbn)
        await execute_query_json(sqlscript, params, needs_commit=True)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="El Libro no fue encontrado")
        raise e
    except Exception as e:
        if "PRIMARY KEY" in str(e):
             raise HTTPException(status_code=400, detail="Este autor ya está asignado")
        if "FOREIGN KEY" in str(e) and "autor" in str(e):
             raise HTTPException(status_code=404, detail=f"El Autor no fue encontrado")
        raise HTTPException(status_code=500, detail=f"Error asignando autor: {str(e)}")
    return {"status": "OK", "mensaje": "Autor asignado"}

# Obtiene los autores de un libro.
async def obtener_autores_de_libro(isbn: str) -> List[Autor]:
    await obtener_libro(isbn)
    sqlscript = """
        SELECT A.[Id_autor], A.[Nombre_autor], A.[Año_nacimiento]
        FROM [biblioteca].[autor] AS A
        INNER JOIN [biblioteca].[libro_autor] AS LA
            ON A.[Id_autor] = LA.[Id_autor]
        WHERE LA.[ISBN] = ?;
    """
    params = [isbn]
    try:
        result = await execute_query_json(sqlscript, params=params)
        if result:
            return json.loads(result)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# Quita un autor de un libro.
async def quitar_autor_de_libro(isbn: str, id_autor: int):
    sqlscript = "DELETE FROM [biblioteca].[libro_autor] WHERE [ISBN] = ? AND [Id_autor] = ?;"
    params = [isbn, id_autor]
    try:
        await execute_query_json(sqlscript, params, needs_commit=True)
        return "ELIMINADO CORRECTAMENTE"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error quitando autor: {str(e)}")
