"""Punto de entrada de la aplicacion."""
import os

from app import create_app
from app.extensions import db
from app import models  # noqa: F401  (registra los modelos)

app = create_app()


@app.shell_context_processor
def _shell_context():
    return {"db": db, "models": models}


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5003))
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=puerto,
            debug=os.getenv("FLASK_DEBUG", "1") == "1")
