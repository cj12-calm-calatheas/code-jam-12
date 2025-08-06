# Documentation

This page provides guidelines for contributing to the documentation.

## Tools

The documentation is built using [MkDocs](https://www.mkdocs.org/), a static site generator that converts Markdown
files into a website.

Markdown is a lightweight markup language with plain-text formatting syntax. Refer to the [Markdown Guide](https://www.markdownguide.org)
for more information on how to use Markdown.

This project uses the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme to generate the
documentation. Please review the theme documentation for guidance on how to use its various features.

## Running the Documentation

!!! NOTE "Prerequisites"

    Ensure you have [set up your development environment](./development-environment.md) before running the documentation.

To view the documentation locally, you can use the following command:

```bash
uv run mkdocs serve
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.

## Adding a New Page

To add a new page to the documentation, create a new Markdown file in the `docs` directory.

Next, update the `nav` section in the `mkdocs.yaml` file to include the new page. The `nav` section defines the
structure of the documentation and the order in which the pages are displayed in the navigation bar.

Please ensure that the folder structure in the `docs` directory matches the structure defined in the `nav` section.

## Linting

This project is configured to use [markdownlint](https://github.com/DavidAnson/markdownlint) to ensure consistent
Markdown styling and formatting across the documentation. The linter is automatically run when you commit changes
to the repository.

You can configure the linter rules in the `.markdownlint.json` file. Refer to the [markdownlint rules](https://github.com/DavidAnson/markdownlint?tab=readme-ov-file#rules--aliases)
for more information on the available rules.

!!! TIP "Use a Markdown Linter Extension"

    We recommend installing a Markdown linter extension in your editor to help identify and fix issues as you write.
    The devcontainer is pre-configured with the [`markdownlint`](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
    extension for Visual Studio Code.

## Formatting

The documentation is formatted using [Prettier](https://prettier.io/), an opinionated code formatter that ensures
consistent style across the project. Prettier is automatically run when you save a Markdown file in the editor.

You can configure the formatting rules in the `.prettierrc.json` file. Refer to the [Prettier options](https://prettier.io/docs/en/options.html)
for more information on the available options.

## Publishing the Documentation

The documentation is published automatically when changes are merged into the `main` branch. A GitHub Action workflow
is triggered to build the documentation and push it to the `gh-pages` branch. The published documentation is hosted
on GitHub Pages.
