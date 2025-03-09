# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

Write-Host "✅ Configuración completa. El entorno virtual está activado."
