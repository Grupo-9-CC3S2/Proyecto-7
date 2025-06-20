#!/bin/bash
# se crea la carpeta backups si no existe
ruta_a_este_script="$(realpath "$0")"
ruta_carpeta_scripts="$(dirname "$ruta_a_este_script")"
ruta_raiz_proyecto="$(dirname "$ruta_carpeta_scripts")"
mkdir -p "$ruta_raiz_proyecto/backups"
# creacion de una copia de terraform.tfstate a backups, se coloca timestamp para diferenciar entre backups
timestamp="$(date +"%Y-%m-%d_%H-%M-%S")"
ruta_terraform_state="$ruta_raiz_proyecto/iac/terraform.tfstate"
# verificar que iac/terraform.tfstate existe
if [ ! -f "$ruta_terraform_state" ]; then
  echo "iac/terraform.tfstate no existe"
  exit 1
fi
# crear carpeta para el nuevo backup y dentro creamos una copia incremental (cambios respecto al backup previo usando rsync --link-dest)
ultimo_backup=$(ls -1dt "$ruta_raiz_proyecto"/backups/tfstate_*.backup/ 2>/dev/null | head -n 1) # buscar ultimo backup
ruta_nuevo_backup="$ruta_raiz_proyecto/backups/tfstate_${timestamp}.backup"
mkdir -p "$ruta_nuevo_backup"
# hacer el backup incremental
if [ -n "$ultimo_backup" ]; then
  rsync -a --link-dest="$ultimo_backup" "$ruta_terraform_state" "$ruta_nuevo_backup/" # si el archivo es igual crea un link al archivo anterior y si es distinto copia un nuevo archivo completo
  echo "se creo un backup incremental"
else
  cp "$ruta_terraform_state" "$ruta_nuevo_backup/"
  echo "se creo un backup inicial"
fi
