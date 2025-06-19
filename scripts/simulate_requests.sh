#!/usr/bin/env bash
# directorio donde caen las peticiones
dest="../balanceador/incoming_requests"
mkdir -p "$dest"

# se crea 10 archivos req_<n>.txt con "petición n"
for i in {1..10}; do
    echo "petición $i" > "$dest/req_${i}.txt"
done

echo "Generadas 10 peticiones en $dest"


