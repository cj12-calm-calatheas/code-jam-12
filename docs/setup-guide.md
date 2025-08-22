# Setup Guide

This guide provides a step-by-step approach on how to run Pokedexter.

## Set up the development environment

Follow the instructions in the [development environment setup guide](./contributor-guide/development-environment.md) to
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

## Local HTTPS for Mobile Testing

You may just want to test the application on a mobile device without setting up a full reverse proxy. Here's how to create a simple, self-signed HTTPS server for local testing.

First, you'll need to create your own SSL/TLS certificate. This certificate will be used to encrypt the connection between your computer and the mobile device. To generate it, run the following command in the project's root directory:

```bash
openssl req -x509 -keyout key.pem -out cert.pem -nodes
```

The command will prompt you for some information. When asked for the "Common Name", enter your computer's local IP address. For all other prompts, press Enter to accept the default values. This process will generate two files in your project's root directory: `key.pem` (your private key) and `cert.pem` (your self-signed certificate).

You can now start the server with the following command:

```bash
uv run uvicorn calm_calatheas.app:app \
  --host "0.0.0.0" \
  --port 4443 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem
```

Because the certificate is self-signed (i.e. not issued by a trusted authority), your browser will likely display a "certificate not trusted" warning. This is expected. You can safely bypass this warning to continue to your application.

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

## Set the environment variables

Pokedexter can be configured using environment variables. The following configuration options are available:

| Environment Variable | Description                             | Default   |
| -------------------- | --------------------------------------- | --------- |
| `HOST`               | The address to bind the server to.      | `0.0.0.0` |
| `LOG_LEVEL`          | The logging level for the application.  | `DEBUG`   |
| `PORT`               | The port to run the server on.          | `8000`    |
| `STATIC_FILES_PATH`  | The path to the static files directory. | `app`     |

!!! NOTE "All settings are optional"

    You can run the app using the default settings without specifying any environment variables.

See the [`Settings`][calm_calatheas.settings.Settings] documentation for more information.

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
name: pokedexter

services:
    reverse-proxy:
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
