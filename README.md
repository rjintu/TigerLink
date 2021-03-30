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

***Note: the site won't fully work until all the database tables are
initialized. There isn't a way to do this automatically yet, but I'll
work on something to fix that soon.***
If you get some database errors while running on our main branch,
chances are your tables aren't configured yet. To create the tables,
you can run the following code:
```python
from database import Database
db = Database()
db.connect()
db.init()
db.disconnect()
```
