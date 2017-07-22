# DSA Membership API

This is the backend for the membership portal.

It uses Auth0 for authentication / authorization and MailGun for sending email.
However these features are disabled by default for local development.

# Common Installation

We use Docker to run and develop the API. Whether you are running the API locally for
developing the UI, or you are making changes to the API, I suggest you use Docker.

1. **[Install docker-compose](https://docs.docker.com/compose/install/)**
2. **Create your `.env` config file for the project**
    ```
    cp example.env .env
    # edit .env and replace the email with your email address
    ```

# Run with Docker

If you don't need to make code changes to the API, the easiest way to get started is to
just use docker compose to run the services. We created a dead-simple command for this:

```
make
```

# Debug with Docker

If you need to make changes to the API, you will need to install the API locally
and use the `make dev` command instead of `make`. This will start the database,
run any necessary migrations, and then start the app in debug mode so that it
will pickup live updates when you save any changes.

# Installation for Mac OS X

1. **Download and install dependencies**
    ```
    brew update
    brew install mysql pyenv
    ```

2. **Download and install python**
    1. Use pyenv to install python 3.6.1
    ```
    pyenv install 3.6.1
    ```
    2. Source the python 
    ```
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    echo 'eval "$(pyenv init -)"' >> ~/.profile
    ```
    3. (Optional) Source your `~/.profile` from your `~/.bashrc` or `~/.zshrc`
    ```
    # Always source the .profile on startup (to be shell agnostic)
    source $HOME/.profile
    ```
    4. You should now be able to see that you are using the shimmed python
    ```
    which python
    # Should be $HOME/.pyenv/shims/python
    ```

3. **Create a virtual environment (venv) for this project** (read more about [python 3 venv](https://packaging.python.org/installing/#creating-virtual-environments))
    ```
    # from inside the repo
    python -m venv .
    ```

4. **Activate the venv**
    ```
    # from inside the repo
    source bin/activate
    ```
    You should now see `(membership_api)` to the left of your prompt in the terminal

5. **Install the python dependencies**
    1. Verify that you are using the correct `pip`
    ```
    which pip
    # should be ./bin/pip
    ```
    2. Install the dev dependencies
    ```
    pip install -r requirements-dev.txt
    ```

6. **Run the server in debug mode**
    ```
    make dev
    ```

7. Verify that your API is up
    ```
    curl http://localhost:8080/health
    # Should see {"health": true}
    ```

Congrats! You did it!

# Troubleshooting

Help! I'm seeing some error. What do I do?

1. **Error** Can't install Python 3.6.1 on Mac OSX, I'm seeing `zlib not available`
**Fix**
Download and install or upgrade XCode, and install the command line tools.
```
xcode-select --install
```

