# Backend

The Pokedexter backend is primarily responsible for serving the machine learning model for generating descriptions and serving
the static files for the frontend application.

## Web Server

The web server is built with [Starlette](https://www.starlette.io/), a lightweight [ASGI](https://en.wikipedia.org/wiki/Asynchronous_Server_Gateway_Interface)
framework for Python web applications. Starlette offers essential features for handling HTTP requests, routing, and middleware,
making it a straightforward choice for our backend. While we considered [FastAPI](https://fastapi.tiangolo.com/), we ultimately
selected Starlette for its simplicity and minimalism.

The server serves static frontend files and exposes two main endpoints:

- **Description Generation:** An endpoint that uses the machine learning model to generate Pokémon descriptions.
- **Healthcheck:** An endpoint for monitoring the server’s status. Used by the Docker container to ensure the service
  is running.

This setup keeps the backend focused and efficient, aligning with our design goals.

## Description Generation

The backend hosts a machine learning model that generates Pokémon descriptions. This model is accessed through the Description
Generation endpoint, allowing the frontend to request descriptions based on captions created in the browser.

We use the [`Qwen/Qwen3-1.7B`](https://huggingface.co/Qwen/Qwen3-1.7B) model, a general-purpose text generator. After
testing various prompts and settings, we found that this model produces high-quality Pokémon descriptions from image captions.
However, the model is quite large. While it can run on a laptop or desktop for limited use, it does not scale well to many
users and user experience will degrade under heavy load.

For best results, we recommend running the model on a machine that has a [GPU with CUDA support](https://en.wikipedia.org/wiki/CUDA#GPUs_supported)
(the oldest version we tested was CUDA 6.5 on an NVIDIA GeForce GTX 1080ti) and 16GB of RAM. In our experience, generating
a description typically takes less than a minute.

We would have preferred to use a more lightweight model that could run directly in the browser. However, the lightweight
models we tested did not generate high-quality Pokémon descriptions. One possible solution would be to fine-tune or train
a smaller model specifically for this task, but this would have required more time and a dataset of high-quality Pokémon
descriptions, which were beyond our resources for the code jam.

## Reverse Proxy

We recommend deploying Pokedexter behind a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) acting as a
[TLS termination proxy](https://en.wikipedia.org/wiki/TLS_termination_proxy). Both the camera and PWA features require
a [secure browser context](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts), which is only available
when the app is served over HTTPS.

!!! DANGER "Secure browser context required"

    The camera and PWA features will not work outside of a secure browser context!

A reverse proxy is not included in our stack, as most users will already have their own solution or use a managed reverse
proxy provided by their cloud platform. The deployment guide includes instructions for setting up a TLS termination proxy
with [Caddy](https://caddyserver.com/).

If you do not have a valid TLS certificate, the app can only be used on `localhost`, since browsers treat it as a secure
context.

## Docker

Pokedexter can be easily deployed using [Docker](https://www.docker.com/). We provide a `Dockerfile` that sets up the necessary
environment and dependencies for running the application. The Docker image includes the web server, the machine learning
model, and all static files needed for the frontend. We do not publish the Docker image to a public registry, so users
will need to build it locally.
