#!/usr/bin/env python

import os
import sys
from fabric.api import local, task
from fabric.context_managers import shell_env


@task
def backup():
    stop_docker_container()
    do_psql_dump()
    bup_init()
    bup_index()
    do_bup_backup()
    start_docker_container()


@task
def restore():
    do_bup_restore()


def do_bup_backup():
    print('Running incremental backup')
    backuped = local('BUP_DIR=$(pwd)/backup bup save -n stashbackup $(pwd)')
    if backuped.return_code != 0:
        print 'An error occurred while backing up. Aborting...'
        sys.exit(1)


def do_bup_restore():
    restored = local('BUP_DIR=$(pwd)/backup bup restore -C stashbackup '
                     'stashbackup/latest/$(pwd)')
    if restored.return_code != 0:
        print 'An error occurred while restoring. Aborting...'
        sys.exit(1)


def bup_init():
    initiated = local('BUP_DIR=$(pwd)/backup bup init')
    if initiated.return_code != 0:
        print 'An error occurred while initiating bup. Aborting...'
        sys.exit(1)


def bup_index():
    indexed = local('BUP_DIR=$(pwd)/backup bup index --exclude-from '
                    '.bup.ignore $(pwd)')
    if indexed.return_code != 0:
        print 'An error occurred while indexing bup. Aborting...'
        sys.exit(1)


def do_psql_dump():
    print 'dumping...'
    dumped = local('docker run -t --rm --link stash_database_1:db '
                   '-v $(pwd):/tmp postgres sh -c \'pg_dump -U stash -h '
                   '"$DB_PORT_5432_TCP_ADDR" -w stash > /tmp/stash.dump\'')

    if dumped.return_code != 0:
        print 'An error occured while dumping database. Aborting...'
        sys.exit(1)

    if not os.path.exists(os.path.join(os.getcwd(), 'dumps')):
        print 'dumps folder not existing yet. Creating...'
        local('mkdir dumps')
    local('mv stash.dump dumps/stash.dump')
    print 'dumped...'


def stop_docker_container():
    print 'stoping...'
    stopped = local('sudo docker-compose stop stash')
    if stopped.return_code != 0:
        print 'An error occurred while stoping container stash. Aborting...'
        sys.exit(1)
    print 'stopped...'


def start_docker_container():
    print 'starting...'
    started = local('sudo docker-compose start stash')
    if started.return_code != 0:
        print 'An error occurred while starting container stash. Aborting...'
        sys.exit(1)
    print 'started...'
