# TigerLink

### Local Environment Setup

Here's some vague instructions for setting up the local environment, in
case anyone needs to redo it in the next few weeks. Instructions are
for Macs only.

First, install Postgres. `brew install postgresql` generally works if
you don't have an M1 Mac, but good luck otherwise lol.

Then, you have to do a bunch of things to get Postgres working properly
with TigerLink. Here's everything that I think you'll need to do:
1. Start the Postgres Server on your computer by running
`pg_ctl –D /usr/local/var/postgres start`. Note: this also has to be done
every time you restart your computer.
2. Get into the Postgres shell. This can be done by running
`psql postgres` in the terminal. 
3. Run `CREATE ROLE tigerlink LOGIN PASSWORD 'xxx';` in the shell to
create the new user for our local TigerLink environment.
4. Run `CREATE DATABASE tldata WITH OWNER = tigerlink;` to create the
database used by TigerLink.
5. (Optional) To directly enter SQL commands into your local database, run
`psql -h localhost -p 5432 -U tigerlink -d tldata`.

Now you're ready to start the server. You can use `runserver.py` in the
same way as in our 333 assignments (or you can use something different
like `gunicorn`). **Note: to get Google authentication working on your
local server, you have to use port 8888.**

If you get database errors while using the main branch, you may need to configure
your tables. To do this, simply run `python utils/dbschema.py` from the TigerLink folder. 

### Using Secret Keys & HTTPS Locally
Our secret keys for Flask and Google OAuth have to not be shared anywhere
accidentally, so we shouldn't add them directly to this GitHub. Instead,
the Heroku deployment has the keys as an environemnt variable, and our
local test servers can use a `keys.py` file to import the required keys.
To get these keys working locally:
* Download keys.py from our Drive folder
* Move keys.py into the "server/" folder in our repository, i.e. exactly
where tigerlink.py is.

Additionally, you might run into trouble when using https://localhost:8888,
since web browsers won't find a verified certificate for the test server.
To ignore this error in Chrome, you can go to 
`chrome://flags/#allow-insecure-localhost` and Enable that option.
