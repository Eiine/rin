#!/bin/bash

# Obtiene la ruta absoluta de donde está este script
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

echo "🚀 Iniciando Rin desde: $PROJECT_DIR"

# Activar el entorno virtual
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo "❌ Error: No se encontró el entorno virtual en $VENV_PATH"
    exit 1
fi

# Lanzar el orquestador
python "$PROJECT_DIR/voice_record.py"
