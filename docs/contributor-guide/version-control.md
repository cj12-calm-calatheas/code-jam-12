# Version Control

Follow the steps below when contributing to the project. These steps ensure that all changes are properly tracked and reviewed.

## Create a New Branch

Always create a new branch for your changes. This makes it easier to handle multiple contributions simultaneously.

??? QUESTION "Why should I create a new branch?"

    Creating a new branch allows you to work on your changes without affecting the `main` branch. This makes it
    easier to collaborate with others and keep the codebase clean.

First, pull the latest changes from the `main` branch:

```bash
git pull main
```

Next, create a new branch with the following command:

```bash
git checkout -b "<YOUR_BRANCH_NAME>"
```

Replace `<YOUR_BRANCH_NAME>` with a short, descriptive name for your branch. For example, `add-uptime-command`.

## Commit your Changes

On your local branch, you can make changes to the code such as adding new features, fixing bugs, or updating documentation.
Once you have made your changes, you can commit them to your branch.

```bash
git add .
git commit -m "feat: add uptime command"
```

Make sure to write a clear and concise commit message that describes the changes you have made.

??? QUESTION "How often should I commit my changes?"

    It's a good practice to commit your changes often. This allows you to track your progress and revert changes if needed.

### Automated Checks

The project includes pre-commit hooks to ensure your code meets the quality standards. These hooks run automatically
before each commit.

??? QUESTION "What if the pre-commit hooks fail?"

    If the pre-commit hooks fail, you will need to address the issues before committing your changes. Follow the
    instructions provided by the pre-commit hooks to identify and fix the issues.

??? QUESTION "How do I run the pre-commit hooks manually?"

    Pre-commit hooks can also be run manually using the following command:

    ```bash
    uv run pre-commit
    ```

The pre-commit hooks are intended to help us keep the codebase maintainable. If there are rules that you believe
are too strict, please discuss them with the team.

## Create a Pull Request

Once you have completed your changes, it's time to create a pull request. A pull request allows your changes to
be reviewed and merged into the `main` branch.

Before creating a pull request, ensure your branch is up to date with the latest changes from the `main` branch:

```bash
git pull main
```

Next, push your changes to the repository:

```bash
git push
```

Finally, [create a pull request on GitHub](https://github.com/cj12-calm-calatheas/code-jam-12/compare). Select
your branch as the source and the `main` branch as the base.

Give your pull request a descriptive title that summarizes the changes you have made. In the pull request description,
provide a brief overview of the changes and any relevant information for reviewers.

??? EXAMPLE "Pull Request Description"

    Here's an example of a good pull request description:

    ```plaintext
    # feat: add uptime command

    This pull request adds a new uptime command to display the bot's uptime.

    ## Changes

    - Added a new command to display the bot's uptime
    - Updated the help command to include information about the new command

    ## Notes

    - The new command is implemented in a separate file for better organization
    - The command has been tested locally and works as expected
    ```

### Automated Checks

The same pre-commit hooks that run locally will also run automatically on the pull request. The workflow also
runs the tests to ensure everything is working correctly, and checks the docs for any broken links.

??? QUESTION "What if the checks fail on the pull request?"

    If the checks fail on the pull request, you will need to address the issues in your branch and push
    the changes. The checks will run again automatically.

    Please address any issues identified by the checks before requesting a review.

## Ask for a Review

All pull requests should be reviewed by at least one other team member before merging. The reviewer will provide
feedback and suggestions for improvement.

Once the reviewer approves the pull request, you can merge it into the `main` branch.

??? QUESTION "How do I request a review?"

    Request a review from a team member by [assigning them as a reviewer](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review)
    to your pull request.

### Giving Feedback

When providing feedback on a pull request, be constructive and specific. Point out areas for improvement and suggest
possible solutions. If you have any questions or concerns, don't hesitate to ask the author for clarification.

A code review should focus on the following aspects:

- Correctness and functionality
- Code quality and readability
- Adherence to the project guidelines

??? EXAMPLE "Good Code Review Feedback"

    Here are some examples of good code review feedback:

    ```plaintext
    - Great work on the new command! The implementation looks good overall.
    - I noticed a small typo in the docstring. Could you update it to fix the typo?
    - The logic in the new command is a bit complex. Consider breaking it down into smaller functions for clarity.
    - The tests cover most of the functionality, but we are missing a test case for edge case X. Could you add a test for that?
    ```

Always be respectful and considerate when giving feedback. Remember that the goal is to improve the code and help
the author grow as a developer.

!!! SUCCESS "Be Positive"

    Don't forget to acknowledge the positive aspects of the contribution as well!

## Merge the Pull Request

Once the pull request has been approved and all checks have passed, you can merge it into the `main` branch.
To merge the pull request, click the "Merge" button on the pull request page. After merging, your branch will be automatically
deleted.
