The docker's configuration file is used in order to create a local
installation of PostgreSQL and convert all the old posts.

```
$ docker build -t postgres .
$ docker run --rm -P --name pg_test pg
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                     NAMES
fa60c060b7d2        pg                  "/usr/lib/postgresql/"   11 seconds ago      Up 10 seconds       0.0.0.0:32769->5432/tcp   pg_test
$ psql -h localhost --port 32769 --user docker
```