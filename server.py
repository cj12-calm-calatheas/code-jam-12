from collections.abc import Awaitable, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

routes = [Mount("/", app=StaticFiles(directory="app", html=True), name="static")]

app = Starlette(routes=routes)


@app.middleware("http")
async def set_pyscript_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Set response headers required by PyScript for workers to function properly."""
    response = await call_next(request)

    headers = response.headers.mutablecopy()

    headers.append("Access-Control-Allow-Origin", "*")
    headers.append("Cross-Origin-Opener-Policy", "same-origin")
    headers.append("Cross-Origin-Embedder-Policy", "require-corp")
    headers.append("Cross-Origin-Resource-Policy", "cross-origin")

    response.init_headers(headers)

    return response
