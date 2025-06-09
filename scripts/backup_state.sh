#!/bin/bash
# se crea la carpeta backups si no existe
ruta_a_este_script="$(realpath "$0")"
ruta_carpeta_scripts="$(dirname "$ruta_a_este_script")"
ruta_raiz_proyecto="$(dirname "$ruta_carpeta_scripts")"
mkdir -p "$ruta_raiz_proyecto/backups"
# creacion de una copia de terraform.tfstate a backups, se coloca timestamp para diferenciar entre backups
timestamp="$(date +"%Y-%m-%d_%H-%M-%S")"
ruta_terraform_state="$ruta_raiz_proyecto/iac/terraform.tfstate"
ruta_nuevo_backup="$ruta_raiz_proyecto/backups/tfstate_${timestamp}.backup"
cp "$ruta_terraform_state" "$ruta_nuevo_backup"