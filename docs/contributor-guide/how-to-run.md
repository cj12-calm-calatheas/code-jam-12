# How to Run

This guide provides a step-by-step approach on how to run Pokedexter.

## Set up the development environment

Follow the instructions in the [development environment setup guide](./development-environment.md) to
set up your local environment.

## Run the app locally

The easiest way to run Pokedexter locally is to use the included [`taskipy`](https://pypi.org/project/taskipy/) configuration.
Run the following command:

```bash
uv run task serve
```

This runs a development server that you can use to access the app from your local machine. This is great for trying out
the app yourself on the device where you are running the server.

Keep reading if you'd like to deploy Pokedexter for production use, or if you'd like to access the app from another device
like a mobile phone or tablet.

## Build the Docker image

The easiest way to deploy Pokedexter is to use [Docker](https://www.docker.com/). To deploy Pokedexter, you must first
build the Docker image.

!!! INFO "Prerequisite"

    Make sure you have [Docker](https://www.docker.com/) installed before proceeding.

The project has a `taskipy` configuration that makes it easy to build the Docker image. Run the following command:

```bash
uv run task build-docker
```

This first builds a `.whl` file for the project, and then uses that file to build the Docker image based on the included
`Dockerfile`. The docker image will be called `calm-calatheas:latest`.

## Run the Docker container

Once the image is built, you can deploy the app to an environment of your choice.

!!! INFO "Minimum system specs"

    For a minimal deployment, we recommend **2 CPU cores** and **8GB of RAM**. We also recommend a GPU with at least
    **4GB of VRAM** and **CUDA 6.5** support or higher.

**If you are deploying Pokedexter to the cloud**, refer to your cloud provider's documentation on how to deploy a Docker
container.

**If you are hosting Pokedexter yourself**, you can run the Docker container with the following command:

```bash
docker run -p 8000:8000 calm-calatheas:latest
```

This runs the container and maps the default port `8000` to the host machine, allowing you to access the app at `http://localhost:8000`.

!!! DANGER "Secure browser context required"

    Both the camera and PWA features require a [secure browser context](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts), which is only available when the app is served over HTTPS or on `localhost`.

    Keep reading if your deployment will be accessed outside of `localhost`.

## Set up a reverse proxy

We recommend deploying Pokedexter behind a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) acting as a
[TLS termination proxy](https://en.wikipedia.org/wiki/TLS_termination_proxy).

!!! INFO "Prerequisite"

    Make sure you have a registered [domain name](https://en.wikipedia.org/wiki/Domain_name) and that you have access
    to the [DNS](https://en.wikipedia.org/wiki/Domain_Name_System) settings for that domain.

**If you are deploying Pokedexter to the cloud**, we recommend that you use your cloud provider's gateway solution to set
up HTTPS for the app.

**If you are hosting Pokedexter yourself**, here's a sample `docker-compose.yaml` file using [Caddy](https://caddyserver.com/):

```yaml
name: Pokedexter

services:
    caddy:
        image: caddy:latest
        command: caddy reverse-proxy --from <your-domain>:8000 --to app:8000
        depends_on:
            app:
                condition: service_healthy
        ports:
            - 8000:8000

    app:
        image: calm-calatheas:latest
        ports:
            - 8000
```

This configuration sets up Caddy as a reverse proxy for your app, allowing you to access it securely over HTTPS. Caddy
will automatically obtain and renew SSL certificates for your domain using [Let's Encrypt](https://letsencrypt.org/).

## Set up DNS

Finally, set up a DNS record for your domain that points to the server where the reverse proxy is running:

```plaintext
Type: A
Host: <your-domain>
Value: <your-server-ip-address>
TTL: 3600
```

Replace `<your-server-ip-address>` with the public IP address of the machine running your reverse proxy. This will direct
traffic for `<your-domain>` to your server.

!!! SUCCESS "Deployment complete"

    You can now access the app from any device at `https://<your-domain>:8000`!
