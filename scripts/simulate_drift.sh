#!/bin/bash

# timestamp para distinguir cada ejecución
timestamp=$(date +%Y-%m-%d_%H-%M-%S)

# modificar un valor en iac/main.tf para forzar drift
sed -i "s/always_run = .*/always_run = \"$timestamp\"/" ../iac/main.tf

# ejecutar terraform plan y guardar log
mkdir -p ../logs

# 4. Entrar en la carpeta iac, correr plan, muestrar y guardar la salida en ../logs
cd ../iac

terraform init -input=false        # ← inicializa sin pedir interacción
terraform plan | tee ../logs/drift_"$timestamp".log

cd ..
echo "Drift simulado: log en logs/drift_$timestamp.log"