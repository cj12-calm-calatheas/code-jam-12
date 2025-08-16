from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from .model import generate_description
from .settings import settings


async def describe(request: Request) -> Response:
    """Handle GET requests to the /describe endpoint."""
    user_prompt = request.query_params.get("prompt", "")

    if not user_prompt:
        return Response("Missing prompt", status_code=400)

    description = generate_description(user_prompt)

    return Response(description.model_dump_json(), media_type="application/json")


async def healthcheck(_: Request) -> Response:
    """Handle GET requests to the /healthcheck endpoint."""
    return Response("OK", media_type="text/plain")


routes = [
    Route("/describe", endpoint=describe, methods=["GET"]),
    Route("/healthcheck", endpoint=healthcheck, methods=["GET"]),
    Mount("/", app=StaticFiles(directory=settings.static_files_path, html=True), name="static"),
]

app = Starlette(routes=routes)
