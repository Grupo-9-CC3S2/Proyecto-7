# Proyecto 7 - Operaciones y recuperación ante desastres locales para infraestructura Terraform

**Integrantes**
- Daren Adiel Herrera Romo (scptx0)
- Renzo Quispe Villena (RenzoQuispe)
- Andre Sanchez Vega (AndreSanchezVega)

## Videos grupales

### Sprint1
- [Video de sprint 1](https://unipe-my.sharepoint.com/:v:/g/personal/daren_herrera_r_uni_pe/EYXxNwB6cb9OmSLQNa7B8q4B7q1i92Xruj1x8dw18KKDHg?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=dMGP9e)

### Sprint 2
- [Video de sprint 2 - Daren Herrera](https://drive.google.com/file/d/1jPPA7qiJpGir4vT4eNaaCHprOUBv8P7Q/view?usp=sharing)
- [Video de sprint 2 - Andre Sanchez](https://drive.google.com/file/d/1dsf3CsWrHlfc4x4EFR3oL97l-DVonTc5/view?usp=sharing)
- [Video de sprint 2 - Renzo Quispe](https://drive.google.com/file/d/17Rh5Ulbk4M2tX8Aw21NVSINUbb9qNJaH/view?usp=sharing)

### Sprint 3
- [Video de sprint 3 - Daren Herrera](https://drive.google.com/file/d/1AGy1jX1GKZ3inboNBuWKUTCsziNMFrt-/view?usp=drive_link)
- [Video de sprint 3 - Andre Sanchez](https://drive.google.com/file/d/1o3VQVK3MyQE-CrOIfd-X3HM050sVBiVC/view)
- [Video de sprint 3 - Renzo Quispe](https://drive.google.com/file/d/1UYIr5GtclGQe9zUyR4IUwAHf4EySOVfX/view?usp=drive_link)

## Descripción general del proyecto

Solución local para manejar el ciclo de vida completo de una infraestructura dummy de Terraform:
- Backup/restauración de estado
- Alta disponibilidad
- Balanceador de carga local en Python
- Simulación de drift
- Gestión de costos simulados mediante scripts bash

## Descripción de scripts

`backup_state.sh`
- Crea una carpeta `backups/`, si no existe, para almacenar todos los archivos de respaldo.
- Se genera el nombre del backup añadiendo un timestamp, con formato `YYYY-MM-DD_HH-MM-SS`, al final.
- Se inserta el estado actual (en el momento de la ejecución del script) del archivo de estado de terraform `terraform.tfstate`. 

`restore_state.sh`
- Lee todos los archivos de respaldo en la carpeta `backups/` y verifica que haya al menos un archivo.
- Muestra una lista de los archivos de respaldo y le pide al usuario escribir el número correspondiente al backup que quiere restaurar.
- Copia el archivo de respaldo a la ruta de `terraform.tfstate` (en `iac/`) y restaura el estado.

`simulate_drift.sh`
- Usa `sed` para cambiar el nombre de uno de los recursos en `iac/main.tf`
- Ejecuta `terraform init` y `terraform plan` para ver el drift.
- Se almacena el drift del estado en un archivo de log en `logs/`.

`cost_saving.sh`
- Según la hora del sistema (24 h), apaga/enciende service_3/
- Esta integrado a balanceador.py, en cada iteración de loop_balanceo(), antes de procesar peticiones, ejecuta cost_saving.sh

`balanceador.py`
- Crea e inicializa servicios.
- Distribuye el procesamiento de los archivos de `incoming_requests`.
- Se ejecuta infinitamente en modo daemon con delay de 5 segundos.
- Realiza un health-check cada 10 segundos para ver que servicios están activos.
- Si hay un error con el procesamiento del archivo, se traslada a `errors/`.
- Crea y actualiza logs que permiten visualizar que archivos ha procesado cada servicio. 

## Estructura del proyecto

```
├── iac/                   # Infraestructura
│   └── main.tf            # Recursos dummy (null_resource)
├── scripts/
│   ├── backup_state.sh    # Script de backup de tfstate con timestamp
│   ├── restore_state.sh   # Script para restauración interactiva
│   ├── cost_saving.sh          # Script para "ahorro de energía"
│   └── simulate_drift.sh   # Script para simular un desplazamiento en el estado
├── balanceador/
│   ├── balanceador.py          # Balanceador (Python)
│   ├── incoming_requests/      # Carpeta para solicitudes
│   ├── logs/                   # Carpeta de logs
│   ├── config_services.json    # Configuración de servicios activos
│   └── settings.json           # Delay de ejecución de balanceador.py
└── tests/
    └── test_balanceador.py     # Script de backup de tfstate con timestamp  
```

## Requisitos técnicos
```
| Herramientas | Versión       |
| Python       | >= 3.10       |
| Terraform    | 1.12.1        |
| Bash         | >= 5.1.16     |
|     jq       | >= 1.6        |
|    rsync     | >= 3.1.0      |
```
## ¿Cómo usar el proyecto?

1. Clonar el repositorio

```bash
git clone https://github.com/Grupo-9-CC3S2/Proyecto-7.git
```

2. Usar los scripts
- `simulate_requests.sh + balanceador.py` 
    ```bash
    make daemon_log
    bash scripts/simulate_requests.sh # tambien con chmod +x y ./
    nohup python balanceador/balanceador.py > balanceador/logs/daemon.log 2>&1 &
    # Usar Ctrl + C para finalizar el proceso
    ```

    Luego de haber iniciado la ejecución del balanceador, podemos insertar archivos en `incoming_requests` y el balanceador los irá leyendo y distribuyendo entre los servicios.
- `backup_state,sh` y `restore_state,sh`
    ```markdown
    # Primero tener iniciado terraform en iac/
    # Dar permisos de ejecucion a los scripts
    chmod +x scripts/backup_state.sh
    chmod +x scripts/restore_state.sh
    # probar scripts con:   
    ./scripts/backup_state.sh
    ./scripts/restore_state.sh
    ```
    Con el script backup_state.sh podemos crear multiples backup de terraform.state, y luego con restore_state.sh podemos listarlos y restaurar terraform.tfstate a un estado anterior.

## Diagrama ASCII del flujo de balanceo y backup/restauración.

### Balanceo

      ```
      [incoming_requests/] 
            |
            v
      [balanceador.py] --(health check)--> [service_1/ service_2/ ...]
            |
            v
      [Renombra y mueve archivo a service_<id>/]
            |
            v
      [logs/load_<n>.json]
            |
            v
      [errors/] (si hay error)
      ```

### Diagramas del proceso de backup/restauración

Creación de backup con backup_state.sh
```
[terraform.tfstate] 
      |
      v
[backup_state.sh] --->  Se crea copia incremental con rsync
                        /backups/tfstate_2025-06-20_18-30-00.backup/terraform.tfstate

Estructura del backup:
/backups/
└── tfstate_2025-06-20_18-30-00.backup/
      └── terraform.tfstate  (copia nueva o hardlink a copia anterior)
```
Simulación de desastre
```
Usuario borra o modifica terraform.state

Estado:
[terraform.tfstate] -->  no existe o esta dañado
```
Restauración con restore_state.sh
```
[restore_state.sh] ---> Lista backups disponibles
      |
      v
se selecciona un backup a traves de un menu: tfstate_2025-06-20_18-30-00.backup
      |
      v
Verifica validez JSON (jq)
      |
      v
Copia archivo de backup al directorio original

Resultado:
[terraform.tfstate] --> restaurado a un estado anterior

```