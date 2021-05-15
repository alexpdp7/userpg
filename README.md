Just a dump wrapper for using PostgreSQL as a user.

Currently it's only been tested to work under Debian 10, as the path to PostgreSQL binaries is hardcoded.

# Install

We recommend installing it using [pipx](https://pipxproject.github.io/pipx/):

```
$ pipx install --spec git+https://github.com/alexpdp7/userpg.git userpg
```

# Usage

```
$ userpg path/to/dump
```

Will start a PostgreSQL instance listening on a UNIX socket.
If `path/to/dump` exists, it will be loaded into the database.
Then it will print something like:

```
psql -h /tmp/tmp1kmc99ly postgres
```

, which is the command you can use to connect to the database.
When you terminate the process (using `kill` or control C), it will dump the database back to `path/to/dump` and stop the database.
