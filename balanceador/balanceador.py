import time
import os
import json

# Ruta en la que se encuentra este script
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_REQUESTS = os.path.join(DIR_BASE, "incoming_requests")
DIR_ERRORS = os.path.join(DIR_BASE, "errors")
DIR_LOGS = os.path.join(DIR_BASE, "logs")
NUM_SERVICIOS = 3


def actualizar_log(i_servicio, nombre_archivo, timestamp):
    """
    Actualiza el archivo de log JSON correspondiente a una instancia de servicio.

    Si el log ya existe, agrega el nuevo archivo procesado a la lista y actualiza
    el timestamp de último procesamiento. Si no existe, crea uno nuevo con la información dada.

    Parámetros:
    - i_servicio (int): Numero de servicio.
    - nombre_archivo (str): Nombre del archivo que fue procesado.
    - timestamp (str): Tiempo local en el que se dio el procesamiento.
    """
    os.makedirs(DIR_LOGS, exist_ok=True)
    ruta_log = os.path.join(DIR_LOGS, f"load_{i_servicio}.json")

    # Verificar si ya existe el log
    if os.path.exists(ruta_log):
        with open(ruta_log, "r", encoding="utf-8") as f:
            datos = json.load(f)
    else:
        datos = {"archivos": [], "ultimo_procesamiento": None}

    datos["archivos"].append(nombre_archivo)
    datos["ultimo_procesamiento"] = timestamp

    # Guardamos el log actualizado
    with open(ruta_log, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)


def procesar_archivos(archivos):
    """
    Procesa los archivos y distribuye la carga (round-robin) entre los servicios, actualizando
    los logs.

    Para cada archivo de la lista "archivos":
    - Valida su contenido
    - Renombra el archivo agregando un prefijo con timestamp.
    - Lo distribuye a los diferentes servicios 'service_<id>/' por round-robin.
    - Actualiza el log correspondiente en 'logs/load_<id>.json'.
    - Si ocurre un error al validar el contenido, mueve el archivo a la carpeta 'errors/'.

    Parámetros:
    - archivos (list[str]): Lista de rutas de los archivos que se quieren procesar
    """
    i = 1
    for archivo in archivos:
        # Solo el nombre del archivo, no una ruta
        nombre_archivo = os.path.basename(archivo)
        ruta_archivo = os.path.join(DIR_REQUESTS, nombre_archivo)
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            # Distribución round-robin entre las carpetas service_<id>/
            # Numero de servicio que maneja la solicitud
            i_servicio = (i - 1) % NUM_SERVICIOS + 1
            carpeta_destino = os.path.join(DIR_BASE, f"service_{i_servicio}")
            os.makedirs(carpeta_destino, exist_ok=True)

            timestamp_archivos = time.strftime(
                "%Y-%m-%d_%H-%M-%S", time.localtime())
            nuevo_nombre_archivo = f"processed_{timestamp_archivos}_{nombre_archivo}"
            # Se mueve el archivo con su nombre nuevo a alguno de los servicios
            os.rename(
                ruta_archivo,
                os.path.join(
                    carpeta_destino,
                    nuevo_nombre_archivo))

            # Actualización de logs en cada carpeta de service_<id>/
            timestamp_logs = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())
            actualizar_log(i_servicio, nuevo_nombre_archivo, timestamp_logs)

        except Exception as e:
            print(
                f"No se pudo procesar el archivo '{nombre_archivo}': {e}. Moviendo a \"errors\"...")
            os.makedirs(DIR_ERRORS, exist_ok=True)
            os.rename(ruta_archivo, os.path.join(DIR_ERRORS, nombre_archivo))

        i += 1


def main():
    try:
        archivos_y_directorios = os.listdir(DIR_REQUESTS)
        # Solo para listar archivos y no directorios
        archivos = [
            f for f in archivos_y_directorios
            if os.path.isfile(os.path.join(DIR_REQUESTS, f))
        ]
        print(f"Archivos a procesar: {archivos}")
        procesar_archivos(archivos)
    except FileNotFoundError:
        print(f"Error: La carpeta {DIR_REQUESTS} no existe")


if __name__ == "__main__":
    main()
