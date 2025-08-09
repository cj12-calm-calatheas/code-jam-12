# Development Environment

Follow the steps below to set up your development environment.

## Configure your SSH Key

Follow the steps below to configure your SSH key for accessing the repository:

1. [Generate an SSH key](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
2. [Add the SSH key to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

## Clone the Repository

To clone the repository, run the following command:

```bash
git clone git@github.com:cj12-calm-calatheas/code-jam-12.git
```

This will clone the repository to your local machine using SSH.

## Environment Setup

To get started with the project, you can either install the [devcontainer](https://containers.dev) or follow the manual
setup instructions below.

### Using the Devcontainer

This project includes a [devcontainer](https://containers.dev) to automatically set up your development
environment, including the all tools and dependencies required for local development.

??? NOTE "Prerequisites"

    Please ensure you have the following prerequisites installed:

    - [Docker](https://www.docker.com) must be installed on your system to use the devcontainer.

    - The [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) for Visual Studio Code must be installed to work with devcontainers.

??? TIP "Use WSL on Windows"

    If you are using Windows, we **strongly** recommend cloning the repository into the [WSL](https://learn.microsoft.com/en-us/windows/wsl/)
    filesystem instead of the Windows filesystem. This significantly improves I/O performance when running the devcontainer.

#### Configure your SSH Agent

The devcontainer will attempt to pick up your SSH key from your `ssh-agent` when it starts. Follow the
guide on [sharing git credentials with the devcontainer](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
to ensure your SSH key is available inside the container.

#### Open the Repository

To get started, navigate to the folder where you cloned the repository and run:

```bash
code .
```

This will open the current directory in Visual Studio Code.

#### Build the Environment

Once Visual Studio Code is open, you will see a notification at the bottom right corner of the window asking if
you want to open the project in a devcontainer. Select `Reopen in Container`.

Your development environment will now be set up automatically.

??? QUESTION "What if I don't see the notification?"

    You can manually open the devcontainer by pressing `F1` to open the command pallette. Type
    `>Dev Containers: Reopen in Container` and press `Enter` to select the command.

??? EXAMPLE "Detailed Setup Guides"

    For more details, refer to the setup guide for your IDE:

    - [Visual Studio Code](https://code.visualstudio.com/docs/devcontainers/tutorial)
    - [PyCharm](https://www.jetbrains.com/help/pycharm/connect-to-devcontainer.html)

### Manual Setup

Alternatively, you can set up the development environment manually by following the steps below.

??? NOTE "Prerequisites"

    Please ensure you have the following prerequisites installed:

    - [Python 3.13](https://www.python.org/downloads/) must be installed on your system.
    - [Node.js](https://nodejs.org) must be installed on your system for linting non-Python files.

    You can check your Python version with:

    ```bash
    python --version
    ```

#### Open the Repository

Start by opening the repository in your terminal or command prompt.

```bash
cd path/to/your/repository
```

#### Set up your Python Environment

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. If you don't have `uv` installed, you can
install it using pip:

```bash
python -m pip install uv
```

To install the dependencies, run:

```bash
uv venv --allow-existing && uv sync
```

This sets up a virtual environment and installs all required packages.

#### Install Node.js Dependencies

For linting non-Python files, we also require some Node.js dependencies. To install them, run:

```bash
npm install
```

#### Set up Pre-commit Hooks

To ensure code quality, this project uses pre-commit hooks. Install them by running:

```bash
uv run pre-commit install
```

This will set up the pre-commit hooks to run automatically on each commit.

#### Install Playwright

This project uses [Playwright](https://playwright.dev/python/) to simulate user interactions for testing. To install the
required dependencies, run the following command:

```bash
uv run playwright install --with-deps
```
