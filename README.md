# DSA Membership API

This is the backend for the membership portal.

It uses Auth0 for authentication / authorization and MailGun for sending email.
**NOTE: Currently, there is a bug when developing locally with these services disabled.**
We are working on a fix so that you can set a flag to disable Auth0 and not need to be authenticated
to use the site.
 
# Installation for Mac OS X

**1. Download and install Python3**
```
brew update
brew install python3
```
2. (NOTE) If you see the error `zlib not available`
  a. Download and install or upgrade XCode, and install the command line tools
  ```
  xcode-select --install
  ```
  b. After you have installed python 3.6.1, you should be able verify this with
  ```
  python3 -V
  # should be >= 3.6.1
  ```
**3. Create a virtual environment (venv) for this project** (read more about [python 3 venv](https://packaging.python.org/installing/#creating-virtual-environments))
```
# from inside the repo
python3 -venv .
```
  a. Verify that you have the python 3.6.1 configured in venv
  ```
  cat pyvenv.cfg
  # should show version = 3.6.1
  ```
4. (NOTE) If you don't see `(membership_api)` to the left of your prompt
  a. Activate the venv
  ```
  # from inside the repo
  bin/activate
  ```
  b. You should now see `(membership_api)` to the left of your prompt in the terminal
**5. Verify that you are using the correct `pip`**
```
which pip
# should be ./bin/pip
```
**6. Install the development dependencies**
```
pip install -r requirements-dev.txt
```
**7. Create your `.env` config file for the project**
```
cp example.env .env
# edit .env and replace the email with your email address
```
**8. Run the database migrations**
```
PYTHONPATH=. alembic upgrade head
```
  a. (NOTE) If you don't have mysql installed run
  ```
  brew install mysql
  ```
  b. (NOTE) If you can't connect to the mysql socket `/tmp/mysql.sock`, you need to start the server
  ```
  mysql.server start
  ```
  c. (NOTE) If you see an error about a missing the `dsa` database, create it with
  ```
  mysql -u root -e "create database dsa"
 ```
**8. Create your `.env` config file for the project**
```
cp example.env .env
# edit .env and replace the email with your email address
```
**9. Run the server**
```
make run
```
10. Verify that your API is up
```
curl http://localhost:8080/health
# Should see {"health": true}
```

Congrats! You did it!
