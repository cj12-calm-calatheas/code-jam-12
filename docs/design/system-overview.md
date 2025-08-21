# System Overview

The diagram below illustrates the architecture of the Pokedexter system:

![System Overview](../assets/design/overview.drawio)

Most of the system runs in the browser, using technologies such as PyScript and Pyodide, and makes extensive use of browser
APIs. Features like object recognition and the database, which are often implemented as backend services, are handled in-browser
where possible.

The backend is intentionally minimal to align with our design goals and the code jam theme. It mainly serves static frontend
assets and processes tasks that cannot be handled in the browser due to resource constraints.
