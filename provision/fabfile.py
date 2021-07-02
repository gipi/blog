import os
import hashlib
import tempfile
import shlex
import tarfile
import subprocess
import invoke
from pathlib import Path
from fabric import task
from patchwork import files


PROJECT_ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
REMOTE_REVISION = None
RELEASES_RELATIVE_PATH_DIR = 'releases'


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


def describe_revision(c, head='HEAD'):
    with c.prefix('cd %s' % PROJECT_ROOT_DIR):
        actual_tag = c.run('git describe --always %s' % head)
        return actual_tag.stdout.strip('\n')

def get_release_filename(c):
    return '%s.tar.gz' % describe_revision(c)

def get_release_filepath(c):
    return os.path.join(PROJECT_ROOT_DIR, RELEASES_RELATIVE_PATH_DIR, get_release_filename(c))

def get_generated_webroot(base_dir):
    return os.path.join(base_dir, 'output')


@invoke.task
def create_release_archive(c, head='HEAD'):
    # TODO: add VERSION file
    c.config['run']['replace_env'] = False  # workaround
    with c.prefix('cd %s' % PROJECT_ROOT_DIR):
        tempdir = tempfile.mkdtemp()
        c.run('git --work-tree=%s checkout -f %s' % (
            tempdir,
            head,
        ))
        c.run('cd %s && nikola build -a' % tempdir)
        c.run('mkdir -p %s' % RELEASES_RELATIVE_PATH_DIR)
        c.run('tar czf %s -C %s .' % (
            get_release_filepath(c),
            get_generated_webroot(tempdir),
        ))
        c.run('rm -fr %s && echo removed temporary directory' % tempdir)

# https://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
def hashfile(afile, hasher, blocksize=65536):
    with open(afile, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)

    return hasher.hexdigest()

@task
def _release(c, path_archive, revision=None, web_root=None, **kwargs):
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

    cwd = c.run('pwd').stdout.strip('\n') if not web_root else web_root


    if not os.path.exists(path_archive):
        raise CommandFailed('Archive \'%s\' doesn\'t exist' % path_archive)

    revision = hashfile(path_archive, hashlib.sha256())
    filename_dest = os.path.basename(path_archive)

    app_dir = os.path.join(cwd, 'app-%s' % revision)
    app_symlink = os.path.join(cwd, 'app')

    c.put(local=path_archive, remote=filename_dest)

    try:
        # if exists remove dir
        if files.exists(c, app_dir):
            c.run('rm -vfr %s' % (
                app_dir,
            ))
        # create the remote dir
        c.run('mkdir -p %s' % app_dir)
        c.run('tar xf %s -C %s' % (
            filename_dest,
            app_dir,
        ))
        # find the previous release and move/unlink it
        is_symlink = c.run('readlink %s' % app_symlink).stdout.strip('\n') != ''
        if files.exists(c, app_symlink) and is_symlink:
            # TODO: move old deploy in an 'archive' directory
            previous_deploy_path = c.run('basename $(readlink -f %s)' % app_symlink).stdout.strip('\n')
            idx = previous_deploy_path.index('-')
            previous_revision = previous_deploy_path[idx + 1:]

            if previous_revision != revision:
                c.run('unlink %s' % app_symlink)
                c.run('mkdir -p old && mv -f %s old/' % previous_deploy_path)

        elif files.exists(c, app_symlink):
            raise CommandFailed('app directory already exists and is not a symlink')

        c.run('ln -s %s %s' % (app_dir, app_symlink))

    except CommandFailed as e:
        print('An error occoured: %s' % e)

    print ('''

    %s --> %s

''' % (previous_revision or '?', revision))

@task
def nikola_deploy(c, head='HEAD', web_root=None):
    # locally we create the archive with the app code
    create_release_archive(c, head)  # cannot use pre=[...] because doesn't work
    release_filename = get_release_filename(c)

    local_release_filepath = get_release_filepath(c)

    _release(c, local_release_filepath, revision=head)

@task
def shell(c, revision=None):
    '''Open a shell into an app's environment (the enabled one as default)'''
    cwd = c.run('pwd').stdout

    c.run('cd %s' % (
        'app' if not revision else ('app-%s' % revision),
    ))
    c.run('/bin/bash', pty=True)

def get_remote_revision(user):
    global REMOTE_REVISION

    if not REMOTE_REVISION:
        current_app_dir = esudo('cd && basename $(readlink -f app)', user=user)
        try:
            _, REMOTE_REVISION = current_app_dir.split('-')
        except Exception as e:
            print(e)
            REMOTE_REVISION = 'unknown'

    return REMOTE_REVISION

