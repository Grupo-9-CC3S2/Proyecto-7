#!/bin/bash

# scripts/cost_saving.sh — apaga/enciende service_3 según hora del día

#Calcula rutas base
BASE="$(cd "$(dirname "$0")" && pwd)"          # …/Proyecto-7/scripts
BAL_DIR="$BASE/../balanceador"                # …/Proyecto-7/balanceador
SERVICE="$BAL_DIR/service_3"                  # carpeta servicio 3
ARCHIVE_ROOT="$BASE/../archived"              # …/Proyecto-7/archived
ARCHIVE="$ARCHIVE_ROOT/service_3"             # …/Proyecto-7/archived/service_3
LOG="$BAL_DIR/logs/cost.log"                  # archivo de historial de costos

#Asegura carpetas de archive y logs
mkdir -p "$ARCHIVE_ROOT"
mkdir -p "$(dirname "$LOG")"

#Lee hora y minuto en 24h
HOUR=$(date +%H)
MIN=$(date +%M)

#Decide acción según horario
#    - apagar entre 00:00 y 06:00 (inclusive)
#    - encender entre 06:01 y 23:59
if [ "$HOUR" -lt 6 ] || { [ "$HOUR" -eq 6 ] && [ "$MIN" -eq 0 ]; }; then
    # Apagar: mueve service_3/ a archived/
    if [ -d "$SERVICE" ]; then
        mv "$SERVICE" "$ARCHIVE"
        echo "$(date '+%Y-%m-%d %H:%M:%S')  Apagado service_3" >> "$LOG"
    fi
else
    # Encender: restaura si está archivado
    if [ ! -d "$SERVICE" ] && [ -d "$ARCHIVE" ]; then
        mv "$ARCHIVE" "$SERVICE"
        echo "$(date '+%Y-%m-%d %H:%M:%S')  Encendido service_3" >> "$LOG"
    fi
fi
