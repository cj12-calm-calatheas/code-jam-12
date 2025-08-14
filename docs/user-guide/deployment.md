# Deployment

This is the deployment guide for the Calm Calatheas project. It is intended for developers and the code jam judges to understand
the deployment process and requirements.

!!! Prerequisites

    Please ensure that [Docker](https://www.docker.com) is installed on your machine.

## Distribution

The application is intended to be run as a Docker container. You can either pull the image from the GitHub Container Registry
or build it yourself.

### Pull from GHCR

Run the following command to pull the Docker image from the [GitHub Container Registry](https://github.com/orgs/cj12-calm-calatheas/packages/code-jam-12):

```bash
docker pull ghcr.io/cj12-calm-calatheas/code-jam-12:latest
```

This pulls the latest version of the Docker image to your local machine. If you need a previous version, replace the `latest`
tag with the desired version number.

### Build from Source

If you prefer to build the Docker image from the source code, follow these steps:

#### Clone the Repository

First, clone the repository to your local machine:

```bash
git clone git@github.com:cj12-calm-calatheas/code-jam-12.git
```

Next, open the project directory in your terminal or using your favorite editor.

#### Build the Docker Image

Once you are in the project directory, you can build the Docker image using the following command:

```bash
docker build -t ghcr.io/cj12-calm-calatheas/code-jam-12:latest .
```

This command will build the Docker image and tag it as `ghcr.io/cj12-calm-calatheas/code-jam-12:latest`. You can replace
`latest` with a specific version number if needed.

## Run the Docker Container

Once you have the Docker image, you can run the application in a Docker container using the following command:

```bash
docker run -d -p 8000:80 ghcr.io/cj12-calm-calatheas/code-jam-12:latest
```

This command will run the Docker container in detached mode (`-d`) and map port 80 of the container to port 8000 on your
host machine. You can access the application by navigating to `http://localhost:8000` in your web browser.

## Set up HTTPS

!!! WARNING "App requires secure browser context"

    The application requires a secure browser context to function properly. This means that it should be accessed over HTTPS or on `localhost`.

    Keep reading if you are planning to access the app from another device (such as your phone), or if you plan to host the app for use by others. If you are only planning to access the the app on `localhost`, you can skip this step.

The Docker image for the app is based on the [NGINX image](https://hub.docker.com/_/nginx). To set up HTTPS, you will need
to configure NGINX with a valid SSL certificate. You can use a self-signed certificate for local development or obtain a
certificate from a trusted Certificate Authority (CA) for production use.

We recommend using [Let's Encrypt](https://letsencrypt.org) for obtaining SSL certificates, as it provides free certificates
and is widely trusted. Please follow [this guide](https://macdonaldchika.medium.com/how-to-install-tls-ssl-on-docker-nginx-container-with-lets-encrypt-5bd3bad1fd48)
to set up Let's Encrypt with your NGINX container.
