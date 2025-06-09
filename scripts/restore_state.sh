#!/bin/bash
# Este script muestra la lista de los archivos backup y permita elegir uno mediante un menu y lo copia en iac/terraform.tfstate
# rutas necesarias para el script
ruta_a_este_script=$(realpath "$0")
ruta_carpeta_scripts=$(dirname "$ruta_a_este_script")
ruta_raiz_proyecto=$(dirname "$ruta_carpeta_scripts")
ruta_carpeta_backups="$ruta_raiz_proyecto/backups"
ruta_terraform_state="$ruta_raiz_proyecto/iac/terraform.tfstate"
# verificar que la carpeta de backups existe
if [ ! -d "$ruta_carpeta_backups" ]; then
  echo "la carpeta de backups no existe"
  exit 1
fi
# lista de los archivos_backups que hay en la carpeta backups
archivos_backups=($(ls "$ruta_carpeta_backups"))
numero_backups=${#archivos_backups[@]}
# verificar si hay archivos backup
if [ "$numero_backups" -eq 0 ]; then
  echo "No se encontraron archivos backups"
  exit 1
fi
# menu de backups para escoger
echo "Lista de backups"
for i in "${!archivos_backups[@]}"; do
  numero=$((i+1))
  echo "$numero- ${archivos_backups[$i]}"
done
# leer la opcion escogida
while true; do
  read -p "Escribe la opcion del backup que quieres restaurar: " opcion
  # verificar que el valor ingresado sea valido
  if [[ "$opcion" =~ ^[0-9]+$ ]]; then  # uso de expresion regular para validar que la entrada se un numero entero positivo
    if [ "$opcion" -ge 1 ]; then
      if [ "$opcion" -le "$numero_backups" ]; then
        break
      else
        echo "no existe esa opcion"
      fi
    else
      echo "no existe esa opcion"
    fi
  else
    echo "no existe esa opcion, ingresar un numero valido"
  fi
done
# copiar el backup escogido a iac/terraform.tfstate
backup_escogido="${archivos_backups[$((opcion-1))]}"
ruta_backup_escogido="$ruta_carpeta_backups/$backup_escogido"
cp "$ruta_backup_escogido" "$ruta_terraform_state"
echo "backup realizado"

