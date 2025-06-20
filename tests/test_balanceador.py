import os
import json
import shutil
import pytest

import balanceador.balanceador as balanceador

DIR_BASE = balanceador.DIR_BASE
DIR_REQUESTS = balanceador.DIR_REQUESTS
DIR_ERRORS = balanceador.DIR_ERRORS
DIR_LOGS = balanceador.DIR_LOGS

@pytest.fixture(scope="module", autouse=True)
def setup_entorno():
    # Setup. Se remueven las carpetas de requests, errores y logs que pueden haber quedado.
    shutil.rmtree(DIR_REQUESTS, ignore_errors=True)
    shutil.rmtree(DIR_ERRORS, ignore_errors=True)
    shutil.rmtree(DIR_LOGS, ignore_errors=True)
    for i in range(1, 4):
        shutil.rmtree(os.path.join(DIR_BASE, f"service_{i}"), ignore_errors=True)

    os.makedirs(DIR_REQUESTS, exist_ok=True) # Se crea la carpeta "incoming_requests/"

    # Configuración dummy de servicios (1 y 2 activos)
    config = {
        "num_servicios": 3,
        "servicios_activos": [1, 2]
    }
    with open(os.path.join(DIR_BASE, "config_services.json"), "w", encoding="utf-8") as f:
        json.dump(config, f)

    yield
    
    # Teardown
    shutil.rmtree(DIR_REQUESTS, ignore_errors=True)
    shutil.rmtree(DIR_ERRORS, ignore_errors=True)
    shutil.rmtree(DIR_LOGS, ignore_errors=True)
    for i in range(1, 4):
        shutil.rmtree(os.path.join(DIR_BASE, f"service_{i}"), ignore_errors=True)


def test_inicializar_servicios():
    balanceador.inicializar_servicios()

    # Se lee la configuración
    with open(os.path.join(DIR_BASE, "config_services.json"), "r", encoding="utf-8") as f:
        config = json.load(f)

    for i in range(1, config["num_servicios"] + 1):
        ruta = os.path.join(DIR_BASE, f"service_{i}")
        assert os.path.isdir(ruta), f"Carpeta service_{i} debió ser creada, pero no lo fue."

        # Verifica que los servicios activos tengan los "archivos activadores" y los inactivos, no.
        archivo_activador = os.path.join(ruta, f"service_{i}.txt")
        if i in config["servicios_activos"]:
            assert os.path.exists(archivo_activador), f"service_{i}.txt debería existir"
        else:
            assert not os.path.exists(archivo_activador), f"service_{i}.txt no debería existir"

def test_procesar_archivo_valido():
    # Se crea un archivo dummy
    archivo_dummy = "prueba.txt"
    ruta_archivo = os.path.join(DIR_REQUESTS, archivo_dummy)
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write("contenido")

    balanceador.procesar_archivos()

    # Se lee la configuración
    with open(os.path.join(DIR_BASE, "config_services.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    servicios_activos = config["servicios_activos"]

    # Se verifica si el archivo se movió correctamente a algún servicio activo
    encontrado = False
    for i in servicios_activos:
        carpeta_servicio = os.path.join(DIR_BASE, f"service_{i}")
        archivos = os.listdir(carpeta_servicio)
        if (archivo_dummy in f for f in archivos):
            encontrado = True
            break
    assert encontrado, "El archivo no fue procesado por alguno de los servicios activos"

    # Se verifica que se hayan generado logs
    log_valido = False
    for i in servicios_activos:
        ruta_log = os.path.join(DIR_LOGS, f"load_{i}.json")
        if os.path.exists(ruta_log):
            with open(ruta_log, "r") as f:
                datos = json.load(f)
                if any(archivo_dummy in archivo for archivo in datos["archivos"]):
                    log_valido = True
                    break
    assert log_valido, "El archivo no fue registrado en ningún log"

def test_procesar_sin_servicios_activos():
    # Cambiar config para no tener servicios activos
    config = {
        "num_servicios": 3,
        "servicios_activos": []
    }
    with open(os.path.join(DIR_BASE, "config_services.json"), "w", encoding="utf-8") as f:
        json.dump(config, f)

    balanceador.inicializar_servicios()

    with open(os.path.join(DIR_REQUESTS, "no_servicios.txt"), "w") as f:
        f.write("contenido")

    balanceador.procesar_archivos()

    # Debe seguir en la carpeta original, ya que no fue procesado
    assert os.path.exists(os.path.join(DIR_REQUESTS, "no_servicios.txt"))
