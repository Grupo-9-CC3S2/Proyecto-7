import time
import os
import json
import threading
import subprocess

# Ruta en la que se encuentra este script
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_REQUESTS = os.path.join(DIR_BASE, "incoming_requests")
DIR_ERRORS = os.path.join(DIR_BASE, "errors")
DIR_LOGS = os.path.join(DIR_BASE, "logs")
DIR_SETTINGS = os.path.join(DIR_BASE, "settings.json")
SCRIPT_COST = os.path.join(DIR_BASE, "..", "scripts", "cost_saving.sh")

NUM_SERVICIOS = 0
SERVICIOS_ACTIVOS = 0


def inicializar_servicios():
    """
    Lee la configuración de servicios y define cuantos hay y cuales están activos.

    Crea las carpetas 'service_<id>', si no existen, que simulan los servicios que 'procesarán'
    los archivos.

    Además, se 'activan' los servicios definidos en SERVICIOS_ACTIVOS. Se considera un servicio
    activo a una carpeta 'service_<id>/' que, dentro de ella, contenga un archivo
    'service_<id>.txt'.

    Nota: Tener en cuenta que el archivo 'service_<id>.txt' no es un archivo que se procesa.
    Es un archivo 'bandera', por así decirlo, para identificar si un servicio está activo o no.
    """
    global NUM_SERVICIOS
    global SERVICIOS_ACTIVOS

    with open(os.path.join(DIR_BASE, "config_services.json")) as f:
        config = json.load(f)

    NUM_SERVICIOS = config["num_servicios"]
    SERVICIOS_ACTIVOS = config["servicios_activos"]

    for i in range(1, NUM_SERVICIOS + 1):
        carpeta_servicio = os.path.join(DIR_BASE, f"service_{i}")
        os.makedirs(carpeta_servicio, exist_ok=True)

        archivo_activador = os.path.join(carpeta_servicio, f"service_{i}.txt")

        if i in SERVICIOS_ACTIVOS:
            with open(archivo_activador, "w", encoding="utf-8") as f:
                f.write("Activado")
        else:  # Se asegura de que el archivo no esté, ya que el servicio está "inactivo"
            if os.path.exists(archivo_activador):
                os.remove(archivo_activador)


def obtener_servicios_activos():
    """
    Retorna la lista de servicios activos (solo los indices de cada uno).
    """
    activos = []
    for i in range(1, NUM_SERVICIOS + 1):
        carpeta_servicio = os.path.join(DIR_BASE, f"service_{i}")
        archivo_activador = os.path.join(carpeta_servicio, f"service_{i}.txt")
        if os.path.isdir(carpeta_servicio) and os.path.isfile(archivo_activador):
            activos.append(i)
    return activos


def get_delay(default=5):
    # Lee 'delay' de settings.json; si falta o es inválido, usa 'default'
    try:
        with open(DIR_SETTINGS, "r", encoding="utf-8") as f:
            d = json.load(f)
            val = int(d.get("delay", default))
            return val if val > 0 else default
    except Exception:
        return default


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


def procesar_archivos():
    """
    Lee los archivos en incoming_requests/, los procesa y distribuye la carga (round-robin)
    entre los servicios activos, actualizando los logs.

    Para cada archivo de la lista "archivos" leída:
    - Valida su contenido
    - Renombra el archivo agregando un prefijo con timestamp.
    - Lo distribuye a los diferentes servicios 'service_<id>/' por round-robin.
    - Actualiza el log correspondiente en 'logs/load_<id>.json'.
    - Si ocurre un error al validar el contenido, mueve el archivo a la carpeta 'errors/'.
    """

    # Leer archivos
    try:
        archivos_y_directorios = os.listdir(DIR_REQUESTS)
        # Solo para listar archivos y no directorios
        archivos = [
            f for f in archivos_y_directorios
            if os.path.isfile(os.path.join(DIR_REQUESTS, f))
        ]
        print(f"Archivos a procesar: {archivos}")

        servicios_activos = obtener_servicios_activos()
        if not servicios_activos:
            print("No hay servicios activos disponibles.")
            return

        # Procesar archivos
        i = 0
        for archivo in archivos:
            # Solo el nombre del archivo, no una ruta
            nombre_archivo = os.path.basename(archivo)
            ruta_archivo = os.path.join(DIR_REQUESTS, nombre_archivo)
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()

                # Distribución round-robin entre las carpetas service_<id>/
                # Numero de servicio que maneja la solicitud
                i_servicio = servicios_activos[i % len(servicios_activos)]
                carpeta_destino = os.path.join(DIR_BASE, f"service_{i_servicio}")

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

    except FileNotFoundError:
        print(f"Error: La carpeta {DIR_REQUESTS} no existe")


def loop_health_check():
    """
    Realiza una revisión cada 10 segundos sobre qué servicios están activos y cúales
    no. Se imprime dicha información.
    """
    estado_anterior = {}
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cambios = []

        for i in range(1, NUM_SERVICIOS + 1):
            carpeta = os.path.join(DIR_BASE, f"service_{i}")
            activador = os.path.join(carpeta, f"service_{i}.txt")
            activo = os.path.isdir(carpeta) and os.path.isfile(activador)
            estado = "ACTIVO" if activo else "INACTIVO"

            if estado_anterior.get(i) != estado:
                cambios.append(f"[{timestamp}] service_{i} cambió a {estado}")
                estado_anterior[i] = estado

        if cambios:
            os.makedirs(DIR_LOGS, exist_ok=True)
            with open(os.path.join(DIR_LOGS, "health.log"), "a") as f:
                for linea in cambios:
                    f.write(linea + "\n")

        time.sleep(10)


def loop_balanceo():
    # Bucle infinito que procesa peticiones obteniendo el delay de settings.json
    delay = get_delay()          # valor inicial
    while True:
        inicializar_servicios()
        # ejecución del cost-saving 
        subprocess.run(["bash", SCRIPT_COST], check=True)

        #inicializar y procesar
        procesar_archivos()
        time.sleep(delay)        # espera el retardo actual
        delay = get_delay(delay)  # relee settings.json por si cambió


def main():
    print(f"[{time.strftime('%H:%M:%S')}] Balanceador iniciado")
    threading.Thread(target=loop_health_check, daemon=True).start()
    loop_balanceo()


if __name__ == "__main__":
    main()
