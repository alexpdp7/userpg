Like Access, only worse!

`userpg` allows you to run a PostgreSQL database as a user, using diffable text files as a back end storage.

Currently it's only been tested to work under Debian. `userpg` looks for PostgreSQL binaries in `/usr/lib/postgresql/N`.

# Install

We recommend installing it using [pipx](https://pipxproject.github.io/pipx/):

```
$ pipx install --spec git+https://github.com/alexpdp7/userpg.git userpg
```

# Usage

```
$ userpg path/to/backend
```

Will start a PostgreSQL instance listening on a UNIX socket.
If `path/to/backend/schema` exists, then the database will be initialized with all the `.sql` files inside, executed in alphabetical order.
If `path/to/backend/data` exists, then `userpg` will load the database with the data found inside.
Then it will print something like:

```
psql -h /tmp/tmp1kmc99ly postgres
```

, which is the command you can use to connect to the database.
When you terminate the process (using `kill` or control C), it will dump the data back to `path/to/backend/data` and stop the database.

# Known issues

* Sequences probably do not work.
