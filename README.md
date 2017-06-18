# DSA Membership API

This is the backend for the membership portal.

It uses Auth0 for authentication / authorization and MailGun for sending email.
**NOTE: Currently, there is a bug when developing locally with these services disabled.**
We are working on a fix so that you can set a flag to disable Auth0 and not need to be authenticated
to use the site.
 
# Installation for Mac OS X

1. **Download and install dependencies**
    ```
    brew update
    brew install mysql pyenv
    ```
    
2. **Create the dsa mysql database**
    1. Start mysql server
    ```
    mysql.server start
    ```
    2. Create the `dsa` database
    ```
    mysql -u root -e "create database dsa"
    ```

3. **Download and install python**
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

4. **Create a virtual environment (venv) for this project** (read more about [python 3 venv](https://packaging.python.org/installing/#creating-virtual-environments))
    ```
    # from inside the repo
    python -m venv .
    ```

5. **Activate the venv**
    ```
    # from inside the repo
    source bin/activate
    ```
    You should now see `(membership_api)` to the left of your prompt in the terminal

6. **Install the python dependencies**
    1. Verify that you are using the correct `pip`
    ```
    which pip
    # should be ./bin/pip
    ```
    2. Install the dev dependencies
    ```
    pip install -r requirements-dev.txt
    ```

7. **Create your `.env` config file for the project**
    ```
    cp example.env .env
    # edit .env and replace the email with your email address
    ```

8. **Run the database migrations**
    ```
    alembic upgrade head
    ```

9. **Run the server**
    ```
    make run
    ```

10. Verify that your API is up
    ```
    curl http://localhost:8080/health
    # Should see {"health": true}
    ```

Congrats! You did it!

# Troubleshooting

Help! I'm seeing some error. What do I do?

1. **Error** Can't run `alembic upgrade` or start the Flask server.
```
... can't connect to the mysql socket `/tmp/mysql.sock` ...
```
**Fix**
```
mysql.server start
```

2. **Error** Can't install Python 3.6.1, I'm seeing `zlib not available`
**Fix**
Download and install or upgrade XCode, and install the command line tools.
```
xcode-select --install
```

