# etl

A collections of scripts to automate Gen3 metadata processing.


## metadata

```commandline

Usage: metadata [OPTIONS] COMMAND [ARGS]...

  Metadata loader.

Options:
  --gen3_credentials_file TEXT  API credentials file downloaded from gen3
                                profile.  [default: credentials.json]

  --help                        Show this message and exit.

Commands:
  drop-program  Drops empty program
  drop-project  Drops empty project
  empty         Empties project, deletes all metadata.
  load          Loads metadata into project
  ls            Introspects schema and returns types in order.

```


## Some useful shortcuts

```commandline

cat etl/truncate_imported_tables.sql |  dc exec -T postgres psql -U postgres

dc stop peregrine-service ; dc rm -f peregrine-service ; dc up -d peregrine-servhistoryice
dc stop sheepdog-service ; dc rm -f sheepdog-service ; dc up -d sheepdog-service

dc stop portal-service ; dc rm -f portal-service ; dc up -d portal-service
dc logs -f portal-service


```