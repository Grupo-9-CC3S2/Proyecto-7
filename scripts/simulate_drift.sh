#!/bin/bash

# timestamp para distinguir cada ejecución
timestamp=$(date +%Y-%m-%d_%H-%M-%S)

#Para forzar el drfit cambiamos el nombre del recurso "service_1" a "service_1_drift"
# en ../iac/main.tf para que terraform plan detecte una desviación
sed -i 's/resource "null_resource" "service_1"/resource "null_resource" "service_1_drift"/' ../iac/main.tf

# ejecutamos terraform plan y guardamos en log
mkdir -p ../logs

cd ../iac || exit 1 # En el caso de que el cd falle.

#corremos plan, luego mostrar y guardar la salida en ../logs
terraform init -input=false        # ← inicializa sin pedir interacción
terraform plan | tee ../logs/drift_"$timestamp".log

echo "Drift simulado: log en logs/drift_$timestamp.log"