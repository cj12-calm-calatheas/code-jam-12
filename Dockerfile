# Use the official Python image as a base image for building the application
FROM python:3.13 AS build-image

# Set the working directory
WORKDIR /build

# Copy the wheel file into the container.
COPY --chown=root:root --chmod=0755 ./dist/*.whl .

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --target=./ ./*.whl && \
    rm ./*.whl

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.13-slim

# Add image metadata
LABEL org.opencontainers.image.authors="Calm Calatheas"
LABEL org.opencontainers.image.description="This is the app built by the Calm Calatheas team for the Python Discord Code Jam 2025"
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.source=https://github.com/cj12-calm-calatheas/code-jam-12
LABEL org.opencontainers.image.title="Calm Calatheas App"

# Add a non-root user and group
RUN addgroup calm-calatheas && \
    adduser --ingroup calm-calatheas calm-calatheas

# Install required system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y curl

# Set the working directory
WORKDIR /application

# Copy in the static assets for the app
COPY --chown=root:root --chmod=0755 ./app ./app

# Copy in the built dependencies
COPY --chown=root:root --chmod=0755 --from=build-image /build ./

# Switch to the non-root user
USER calm-calatheas

# Set default values for the environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Configure a healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD ["sh", "-c", "curl --fail \"http://localhost:${PORT}/healthcheck\" || exit 1"]

# Start the application
ENTRYPOINT [ "python", "-m", "calm_calatheas" ]
