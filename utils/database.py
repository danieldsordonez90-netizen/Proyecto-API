from dotenv import load_dotenv
import os
import pyodbc
import logging
import json
import asyncio

# Carga las variables de entorno desde el archivo .env para la configuración de la base de datos.
load_dotenv()

# Configuración básica del logging para registrar eventos importantes y errores.
logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)

# Obtención de las credenciales de la base de datos desde las variables de entorno.
driver: str = os.getenv("SQL_DRIVER")
server: str = os.getenv("SQL_SERVER")
database: str = os.getenv("SQL_DATABASE")
username: str = os.getenv("SQL_USERNAME")
password: str = os.getenv("SQL_PASSWORD")

# Construcción de la cadena de conexión para pyodbc.
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

async def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos de manera asíncrona.
    Utiliza la cadena de conexión global y maneja errores de conexión.
    
    Returns:
        pyodbc.Connection: Objeto de conexión a la base de datos.
    
    Raises:
        Exception: Si ocurre un error al intentar conectar a la base de datos.
    """
    try:
        logger.info(f"Intentando conectar a la base de datos...")
        conn = pyodbc.connect(connection_string, timeout=10)
        logger.info("Conexión exitosa a la base de datos.")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Error de conexión a la base de datos: {str(e)}")
        raise Exception(f"Error de conexión a la base de datos: {str(e)}")
    except Exception as e:
         logger.error(f"Error inesperado durante la conexión: {str(e)}")
         raise


async def execute_query_json(sql_template, params=None, needs_commit=False):
    """
    Ejecuta una consulta SQL de forma asíncrona y devuelve los resultados en formato JSON.
    Maneja la conexión, ejecución, y el commit o rollback de transacciones.

    Args:
        sql_template (str): La consulta SQL a ejecutar.
        params (tuple, optional): Parámetros para la consulta SQL para prevenir inyección SQL. Defaults to None.
        needs_commit (bool, optional): True si la consulta modifica datos (INSERT, UPDATE, DELETE). Defaults to False.

    Returns:
        str: Una cadena JSON que representa los resultados de la consulta.
    
    Raises:
        Exception: Si ocurre un error durante la ejecución de la consulta.
    """
    conn = None
    cursor = None
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        param_info = "(sin parámetros)" if not params else f"(con {len(params)} parámetros)"
        logger.info(f"Ejecutando consulta {param_info}: {sql_template}")

        # Ejecuta la consulta con o sin parámetros.
        if params:
            cursor.execute(sql_template, params)
        else:
            cursor.execute(sql_template)

        results = []
        # Si la consulta es un SELECT, procesa los resultados.
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            logger.info(f"Columnas obtenidas: {columns}")
            for row in cursor.fetchall():
                # Convierte tipos de datos no serializables (como bytes) a string.
                processed_row = [str(item) if isinstance(item, (bytes, bytearray)) else item for item in row]
                results.append(dict(zip(columns, processed_row)))
        else:
             logger.info("La consulta no devolvió columnas (posiblemente INSERT/UPDATE/DELETE).")

        # Si la operación requiere un commit, lo realiza.
        if needs_commit:
            logger.info("Realizando commit de la transacción.")
            conn.commit()

        # Devuelve los resultados como una cadena JSON.
        return json.dumps(results, default=str)

    except pyodbc.Error as e:
        logger.error(f"Error ejecutando la consulta (SQLSTATE: {e.args[0]}): {str(e)}")
        # Si hay un error y se necesitaba commit, hace rollback.
        if conn and needs_commit:
            try:
                logger.warning("Realizando rollback debido a error.")
                conn.rollback()
            except pyodbc.Error as rb_e:
                 logger.error(f"Error durante el rollback: {rb_e}")

        raise Exception(f"Error ejecutando consulta: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución de la consulta: {str(e)}")
        raise # Relanza el error inesperado
    finally:
        # Asegura que la conexión y el cursor se cierren correctamente.
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Conexión cerrada.")