import atexit
import os
import pathlib
import subprocess
import time


def initdb(path, bin=None):
    if bin is None:
        bin = locate_bin("initdb")
    subprocess.run([bin, path], check=True)


class Postgres:
    def __init__(self, path, bin=None):
        if bin is None:
            bin = locate_bin("postgres")
        self.path = os.path.abspath(path)
        self.bin = bin
        self.process = subprocess.Popen([self.bin, "-D", self.path, "-k", self.path], start_new_session=True)
        atexit.register(self.stop)
        self.wait_ready()

    def wait_ready(self):
        while True:
            if subprocess.run([locate_bin("psql"), "-h", self.path, "postgres", "-c", "select 1"]).returncode == 0:
                return
            time.sleep(1)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def __del__(self):
        self.stop()

    def psql(self, *args, **extra_opts):
        return subprocess.run([locate_bin("psql"), "-h", self.path, *args], **extra_opts)

    def pg_dump(self, *extra_args):
        subprocess.run([locate_bin("pg_dump"), "-h", self.path, *extra_args, "postgres"])


def locate_bin(bin):
    last_postgres = sorted(list(pathlib.Path("/usr/lib/postgresql/").glob("*")), key=lambda p: int(p.name))[-1]
    return last_postgres / f"bin/{bin}"
