First off, thanks for taking the time to contribute to Ninja-IDE. :heart:

# Contributing to NINJA-IDE
There are many ways to contribute to the development of NINJA-IDE: reporting issues, submitting pull requests and requesting a feature.

## Forking and clonning the repo
### Forking
In your favorite browser, go to [https://github.com/ninja-ide/ninja-ide](https://github.com/ninja-ide/ninja-ide) and click the `Fork` button to get a copy of the Ninja-IDE on your GitHub account.

### Cloning
Clone your personal copy of Ninja-IDE with the following command:
```
$ git clone https://github.com/YOUR-USER/ninja-ide.git
```

Congratulations! :tada:  at this point, you already have a copy of Ninja-IDE source code on his personal computer.

## Setting up the environment
It's time to set up our work environment. For this we are going to create a virtual environment and install the dependencies that Ninja-IDE needs to work, we are also going to install some additional dependencies that will help us in development.

### Creating the virtual environment
```
$ python -m venv YOUR-VENVS-DIR/ninja-ide
```

Activate it with:
```
$ source YOUR-VENVS-DIR/ninja-ide/bin/activate
```

### Installing dependencies
Navigate to Ninja-IDE source code and install dependencies.

```
(ninja-ide)$ cd ninja-ide
(ninja-ide)$ pip install -r requirements.txt
(ninja-ide)$ pip install -r requirements-dev.txt
```

### Running from sources
At the root of the project and with the virtual environment activated, run Ninja-IDE with the following command:

```
(ninja-ide)$ python ninja-ide.py
```

You can execute with more verbosity using the `-v` argument:

```
(ninja-ide)$ python ninja-ide.py -vvv
```

### Running tests
When making changes to the Ninja-IDE source code, it is good practice to run the test suit:

```
(ninja-ide)$ make tests
```

There is also a `make` command for checking the code style:

```
(ninja-ide)$ make pep8
(ninja-ide)$ make flake8
```

Or both in one command:

```
(ninja-ide)$ make lint
```

:tada: You are now ready to contribute to the Ninja-IDE code :tada:

## Last words
Please, in order to maintain order and speed up the review, follow the following rules to the letter before submitting a Pull Request.
- Always create a branch from `develop`. For example:
```
(develop) $ git checkout -b feature/my-awesome-feature
```

- Whenever possible, write commit messages according to [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
- If your pull request contains multiple commits, use `git squash` to squash them into one.

## Work Branches
Even if you have push rights on the ninja-ide/ninja-ide repository, you should create a personal fork and create feature branches there when you need them. This keeps the main repository clean and your personal workflow cruft out of sight.

## Pull Requests
To accelerate the acceptance process of your pull requests, always create a pull request per issue and [link the issue in the pull request](https://github.com/blog/957-introducing-issue-mentions). Be sure to follow our [Code Guidelines](https://github.com/ninja-ide/ninja-ide/wiki/Coding-Guidelines). Pull requests should contain tests whenever possible.
