import os
import signal
import sys
import tempfile

import userpg


def run_database_until_stopped(dump_path):
    with tempfile.TemporaryDirectory() as path:
        userpg.initdb(path)
        postgres = userpg.Postgres(path)
        if(os.path.exists(dump_path)):
            postgres.psql("postgres", "-f", dump_path)
        print(f"psql -h {postgres.path} postgres")

        def term(_, __):
            postgres.pg_dump(dump_path)
            postgres.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, term)
        signal.signal(signal.SIGTERM, term)

        signal.pause()



def main():
    run_database_until_stopped(sys.argv[1])


if __name__ == "__main__":
    main()
