#!/bin/bash

#carpeta donde está este script
BASE="$(cd "$(dirname "$0")" && pwd)"

#ruta destino 
dest="$BASE/../balanceador/incoming_requests"

# Si no existe, crea la carpeta destino
mkdir -p "$dest"

#creamos 10 archivos req_<n>.txt con "petición n"
for i in {1..10}; do
    echo "petición $i" > "$dest/req_${i}.txt"
done

echo "Generadas 10 peticiones en $dest"


