## Atlassian stash

For more information on the app please refere to the offical
Atlassian websites:


- [stash](https://www.atlassian.com/software/stash)

### Prerequisites

TBD

### Deploy/Update the application

    # rebuild the docker images
    $ docker-compose build

    # restart the docker images
    $ docker-compose up -d

    # inspect the logs
    $ docker-compose logs

If you deploy the app for the first time you may need to restore the database
from a backup for each app and adapt the database connection settings!

### Debug (aka. go inside) an image

    # execute a bash shell
    $ docker exec -it stash_stash_1 bash

### First run

If you start this orchestration for the first time, a handy feature is to
import your old data. If you're e.g. moving everything to another server
you can put your database backups into the tmp folder and the db initscript
will pick them up automagically on the first run.

    # move your stash db backup file to tmp (filename is important).
    $ mv stash.dump tmp/stash.dump

    # unpack your stash-home backup archive
    $ tar xzf stash-home.tgz --strip=1 -C home

### Backup the home folders

    $ mkdir -p backup/$(date +%F)
      tar czf backup/$(date +%F)/stash-home.tgz home

### Backup the PostgreSQL data

    # backup the stash database
    $ docker run -it --rm --link atlassian_database_1:db -v $(pwd):/tmp \
        postgres sh -c 'pg_dump -U stash -h "$DB_PORT_5432_TCP_ADDR" \
        -w stash > /tmp/stash.dump'

### Restore the PostgreSQL data

    # restore the stash database backup
    $ docker run -it --rm --link atlassian_database_1:db -v $(pwd):/tmp \
        postgres sh -c 'pg_restore -U stash -h "$DB_PORT_5432_TCP_ADDR" \
        -n public -w -d stash /tmp/stash.dump'

## Restoring with the fabfile or bup

All commands have to be launched from within the root folder of the app.

`/srv/data/stash`

### Show all possible restore points:

`sudo BUP_DIR=$(pwd)/backup bup ls stashbackup`

### Restore latest backup:

With the fabfile:
`sudo fab restore`

Without the fabfile:
`sudo BUP_DIR=$(pwd)/backup bup restore`

### Restore a specific backup:

With the fabfile:
`sudo fab restore:revision='2015-03-26-123711'`

Without the fabfile:
`sudo BUP_DIR=$(pwd)/backup bup restore stashbackup/2015-03-26-123711/$(pwd)`

### Restore to a different folder than stashbackup

By default bup will restore the backup to a folder called stashbackup.
To restore to another folder you can use the -C flag or pass 'destination'
to the fabfile.

With the fabfile:
sudo fab restore:destination='anotherlocation'

Without the fabfile:
sudo BUP_DIR=$(pwd)/backup bup restore -C anotherlocation stashbackup/latest/$(pwd)
