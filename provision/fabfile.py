import hashlib
import tempfile
import shlex
import tarfile
import subprocess
from fabric.contrib.files import is_link
from fabric.utils import abort
import os
from fabric.context_managers import show, settings, cd, prefix, lcd
from fabric.contrib import files
from fabric.operations import run, sudo, get, local, put, open_shell
from fabric.state import env
from fabric.api import task

PROJECT_ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
REMOTE_REVISION = None
RELEASES_RELATIVE_PATH_DIR = 'releases'

env.use_ssh_config = True

# https://gist.github.com/lost-theory/1831706
class CommandFailed(Exception):
    def __init__(self, message, result):
        Exception.__init__(self, message)
        self.result = result

def erun(*args, **kwargs):
    with settings(warn_only=True):
        result = run(*args, **kwargs)
    if result.failed:
        raise CommandFailed("args: %r, kwargs: %r, error code: %r" % (args, kwargs, result.return_code), result)
    return result

def esudo(*args, **kwargs):
    with settings(warn_only=True):
        result = sudo(*args, **kwargs)
    if result.failed:
        raise CommandFailed("args: %r, kwargs: %r, error code: %r" % (args, kwargs, result.return_code), result)
    return result


# http://docs.fabfile.org/en/latest/usage/execution.html#roles

def describe_revision(head='HEAD'):
    with lcd(PROJECT_ROOT_DIR):
        actual_tag = local('git describe --always %s' % head, capture=True)
        return actual_tag

def get_dump_filepath(user, prefix=u'backups'):
    return '%s/%s.sql' % (prefix, get_remote_revision(user))

def get_release_filename():
    return '%s.tar.gz' % describe_revision()

def get_release_filepath():
    return os.path.join(PROJECT_ROOT_DIR, RELEASES_RELATIVE_PATH_DIR, get_release_filename())

def get_generated_webroot(base_dir):
    return os.path.join(base_dir, '_site')

@task
def dump_db_snapshot(db_name, user):
    remote_tmp_file_path = '/tmp/dump_db.sql' # FIXME: use temporary file
    sudo('pg_dump %s > %s' % (db_name, remote_tmp_file_path), user='postgres')
    get(remote_path=remote_tmp_file_path, local_path= get_dump_filepath(user))

def reset_db():
    local('python manage.py reset_db')

@task
def load_db(user):
    local('cat %s | python manage.py dbshell' % get_dump_filepath(user))

@task
def load_db_snapshot(db_name, username):
    dump_db_snapshot(db_name, username)
    reset_db()
    load_db(username)

@task
def create_release_archive(head='HEAD'):
    # TODO: add VERSION file
    with lcd(PROJECT_ROOT_DIR):
        tempdir = tempfile.mkdtemp()
        local('git --work-tree=%s checkout -f %s' % (
            tempdir,
            head,
        ))
        local('cd %s && jekyll build' % tempdir)
        local('mkdir -p %s' % RELEASES_RELATIVE_PATH_DIR)
        local('tar czf %s -C %s .' % (
            get_release_filepath(),
            get_generated_webroot(tempdir),
        ))
        local('rm -fr %s && echo removed temporary directory' % tempdir)

# https://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
def hashfile(afile, hasher, blocksize=65536):
    with open(afile, 'r') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)

    return hasher.hexdigest()

@task
def _release(archive, revision=None, web_root=None, **kwargs):
    '''
    Main task

    its role is to decompress an archive to the web root into a directory
    named 'app-X' where X identifies the revision; by default the revision
    is calculated from the sha256 of the archive when not indicated.

    :param version:
    :param archive:
    :param web_root:
    :param kwargs:
    :return:
    '''
    previous_revision = None

    cwd = erun('pwd').stdout if not web_root else web_root

    if not os.path.exists(archive):
        raise CommandFailed('Archive \'%s\' doesn\'t exist' % archive)

    revision = hashfile(archive, hashlib.sha256())
    remote_filepath = os.path.basename(archive)

    app_dir = os.path.join(cwd, 'app-%s' % revision)
    app_symlink = os.path.join(cwd, 'app')

    put(local_path=archive, remote_path=remote_filepath)

    try:
        # if exists remove dir
        if files.exists(app_dir):
            erun('rm -vfr %s' % (
                app_dir,
            ))
        # create the remote dir
        erun('mkdir -p %s' % app_dir)
        erun('tar xf %s -C %s' % (
            remote_filepath,
            app_dir,
        ))
        # find the previous release and move/unlink it
        if files.exists(app_symlink) and is_link(app_symlink):
            # TODO: move old deploy in an 'archive' directory
            previous_deploy_path = erun('basename $(readlink -f %s)' % app_symlink).stdout
            idx = previous_deploy_path.index('-')
            previous_revision = previous_deploy_path[idx + 1:]

            if previous_revision != revision:
                erun('unlink %s' % app_symlink)
                erun('mkdir -p old && mv -f %s old/' % previous_deploy_path)

        elif files.exists(app_symlink):
            raise CommandFailed('app directory already exists and is not a symlink')

        erun('ln -s %s %s' % (app_dir, app_symlink))

    except CommandFailed as e:
        print 'An error occoured: %s' % e

    print '''

    %s --> %s

''' % (previous_revision or '?', revision)

@task
def jekyll_release(head='HEAD', web_root=None):
    # locally we create the archive with the app code
    create_release_archive(head)
    release_filename = get_release_filename()

    local_release_filepath = get_release_filepath()

    actual_version = describe_revision(head)
    previous_version = None

    _release(local_release_filepath, revision=head)

@task
def shell(revision=None):
    '''Open a shell into an app's environment (the enabled one as default)'''
    cwd = erun('pwd').stdout

    open_shell('cd %s' % (
        'app' if not revision else ('app-%s' % revision),
    ))

def get_remote_revision(user):
    global REMOTE_REVISION

    if not REMOTE_REVISION:
        current_app_dir = esudo('cd && basename $(readlink -f app)', user=user)
        try:
            _, REMOTE_REVISION = current_app_dir.split('-')
        except Exception as e:
            print e
            REMOTE_REVISION = 'unknown'

    return REMOTE_REVISION

