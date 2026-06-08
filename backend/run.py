"""
run.py — Punto de entrada del servidor Flask
Agenda Ecuamatriz

Uso:
    python run.py

Variables de entorno requeridas: ver .env.example
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno antes de cualquier import de la app
load_dotenv()

from app import create_app  # noqa: E402 — importación después de load_dotenv es intencional

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"

    print(f"[Agenda Ecuamatriz] Servidor iniciando en http://{host}:{port}")
    print(f"[Agenda Ecuamatriz] Modo debug: {'activado' if debug else 'desactivado'}")

    app.run(host=host, port=port, debug=debug)
