.PHONY: install test cov daemon_log

PYTHON = python
VENV_ACTIVATE = "venv/Scripts/activate"

install: # Instalar dependencias
	@$(PYTHON) -m venv venv
	@source "$VENV_ACTIVATE"
	@pip install -r requirements.txt

test: # Crea el archivo de configuración de pytest y ejecuta los tests
	@echo "[pytest]" > pytest.ini
	@echo "pythonpath = ." >> pytest.ini
	@echo "Ejecutando pruebas para balanceador.py..."
	@$(PYTHON) -m pytest -v tests/test_balanceador.py

cov: # Cobertura
	@echo "Ejecutando análisis de cobertura de las pruebas de balanceador.py..."
	@$(PYTHON) -m pytest tests/ --cov=balanceador --cov-report=term-missing --cov-fail-under=80

daemon_log: # Antes de ejecutar nohup python balanceador/balanceador.py > balanceador/logs/daemon.log 2>&1 &
	@mkdir -p "balanceador/logs"
	@( cd "balanceador/logs" && touch "daemon.log" )
	
