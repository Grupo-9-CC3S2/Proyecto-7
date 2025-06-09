# Proyecto 7 - Operaciones y recuperación ante desastres locales para infraestructura Terraform

**Integrantes**
- Daren Adiel Herrera Romo (scptx0)
- Renzo Quispe Villena (RenzoQuispe)
- Andre Sanchez Vega (AndreSanchezVega)

## Descripción

Solución local para manejar el ciclo de vida completo de una infraestructura dummy de Terraform:
- Backup/restauración de estado
- Alta disponibilidad
- Balanceador de carga local en Python
- Simulación de drift
- Gestión de costos simulados mediante scripts bash

## Estructura del proyecto

```
├── iac/                   # Infraestructura
│   └── main.tf            # Recursos dummy (null_resource)
├── scripts/
│   ├── backup_state.sh    # Script de backup de tfstate con timestamp
│   └── restore_state.sh   # Script para restauración interactiva
├── balanceador/
│   ├── balanceador.py     # Balanceador (Python)
│   ├── incoming_requests/ # Carpeta para solicitudes
│   ├── service_1/         # Instancia dummy 1
│   ├── service_2/         # Instancia dummy 2
│   └── service_3/         # Instancia dummy 3
└── logs/                  # Registros de operaciones
```

## Requisitos técnicos

## ¿Cómo usar el proyecto?

## Diagrama ASCII del flujo de balanceo y backup/restauración.