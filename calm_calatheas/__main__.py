from uvicorn import run

from calm_calatheas import app, settings

run(app=app, host=settings.host, port=settings.port)
