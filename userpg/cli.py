import dataclasses
import pathlib
import signal
import io
import subprocess
import sys
import tempfile
import typing

import yaml

import userpg


def run_database_until_stopped(db_path: pathlib.Path):
    with tempfile.TemporaryDirectory() as path:
        userpg.initdb(path)
        postgres = userpg.Postgres(path)
        schema_path = db_path / pathlib.Path("schema")
        data_path = db_path / pathlib.Path("data")
        if schema_path.exists():
            for schema_file in sorted(schema_path.glob("**/*.sql")):
                postgres.psql("postgres", "-f", schema_file)
        if data_path.exists():
            dump = io.StringIO()
            _convert_data_to_sql(postgres, data_path, dump)
            postgres.psql("postgres", input=dump.getvalue(), encoding='utf8')
        print(f"psql -h {postgres.path} postgres")

        def term(_, __):
            _dump_data(postgres, data_path)
            postgres.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, term)
        signal.signal(signal.SIGTERM, term)

        signal.pause()


def _convert_data_to_sql(pg: userpg.Postgres, data_path: pathlib.Path, out):
    out.write("begin deferrable;\n")
    out.write("set constraints all deferred;\n")
    for schema in data_path.glob("*"):
        for table_path in schema.glob("*.yml"):
            table = table_path.name[:-len(".yml")]
            with open(table_path, encoding="utf8") as f:
                rows = yaml.load(f, Loader=yaml.SafeLoader)
                if not rows:
                    continue
                columns = ", ".join([column for (column, _) in rows[0]])
                out.write(f"COPY {schema.name}.{table} ({columns}) FROM stdin;\n")
                for row in rows:
                    values = "\t".join([data for (_, data) in row])
                    out.write(values)
                    out.write("\n")
                out.write("\\.")
                out.write("\n")
    out.write("commit;\n")


def _dump_data(pg: userpg.Postgres, data_path: pathlib.Path):
    with tempfile.TemporaryDirectory() as temp_dump_path:
        pg.pg_dump("-f", temp_dump_path, "-F", "d", "--compress",  "0")
        toc = subprocess.run(["pg_restore", "-l", temp_dump_path, "-a", "-F", "d"], stdout=subprocess.PIPE, encoding='utf8')
        toc = _parse_toc(toc.stdout)
        for toc_entry in toc:
            columns = _get_table_columns(pg, toc_entry.schema, toc_entry.name)
            _process_toc_entry(toc_entry, columns, pathlib.Path(temp_dump_path), data_path)


@dataclasses.dataclass
class _TocEntry:
    index: int
    schema: str
    name: str
    owner: str


def _get_table_columns(pg: userpg.Postgres, schema: str, table: str) -> typing.List[str]:
    return pg.psql("postgres", "-c", f"select column_name from information_schema.columns where table_schema = '{schema}' and table_name = '{table}' order by ordinal_position", "-t", "-A", stdout=subprocess.PIPE, encoding='utf8').stdout.splitlines()


def _process_toc_entry(toc_entry: _TocEntry, columns: typing.List[str], temp_dump_path: pathlib.Path, data_path: pathlib.Path):
    input_path = temp_dump_path / f"{toc_entry.index}.dat"
    output_path = data_path / toc_entry.schema / f"{toc_entry.name}.yml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _process_data(toc_entry, columns, input_path, output_path)


def _process_data(toc_entry: _TocEntry, columns: typing.List[str], input_path: pathlib.Path, output_path: pathlib.Path):
    rows = []
    with open(input_path) as input:
        for line in input.read().splitlines():
            if line == "\\.":
                break
            data = line.split("\t")
            row = []
            for column, value in zip(columns, data):
                row.append([column, value])
            rows.append(row)
    with open(output_path, "w", encoding="utf8") as output:
        yaml.dump(rows, output)


def _parse_toc(toc_str: str) -> typing.List[_TocEntry]:
    toc = []
    for line in toc_str.splitlines():
        print(line)
        if line.startswith(";"):
            continue
        index_with_colon, _, _, object_type, _, schema, name, owner = line.split(" ")
        if object_type != "TABLE":
            continue
        index = int(index_with_colon[:-1])
        toc.append(_TocEntry(index, schema, name, owner))
    return toc


def main():
    run_database_until_stopped(pathlib.Path(sys.argv[1]))


if __name__ == "__main__":
    main()
