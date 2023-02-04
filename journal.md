# Journal
## Initial commit
Copy the code from Jetbrain's trivia repository, write a README and begin the refactoring journal.
## Code format and first CI workflow
The first obvious way to improve the readability of a codebase is to use a code formatter.
I choose the uncompromising opinionated [black](https://github.com/psf/black).

Code formatting is important to ensure a consistent style across the entire code base for all the project's life.
The simple quoted strings have been replaced by double-quoted ones for example.

In order to unsure the code formatter is going to be used systematically before each commit, I install [pre-commit](https://pre-commit.com/).

I also add a [Github Actions](https://docs.github.com/en/actions) workflow to unsure each pushed commit is correctly formatted.
