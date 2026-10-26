# SPDX-License-Identifier: GPL-3.0-or-later

"""Publish completed exports without truncating a previous destination."""

from contextlib import contextmanager
import os
import errno
import stat
import tempfile


@contextmanager
def izom_propui_free_atomic_output_path(filepath):
    # Follow an existing symlink just as open(..., 'w') does. Do not create
    # missing parent directories: exporting must retain its existing contract.
    target = os.path.realpath(os.fspath(filepath))
    directory = os.path.dirname(target)
    mode = stat.S_IMODE(os.stat(target).st_mode) if os.path.exists(target) else None
    if mode is not None and not mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        raise PermissionError(errno.EACCES, 'Destination is read-only', target)
    # A private staging directory protects unfinished data while the caller's
    # normal open() creates the file with the user's umask/default permissions.
    # mkstemp() would instead change every new POSIX export to mode 0600.
    temporary_dir = tempfile.mkdtemp(prefix=f'.{os.path.basename(target)}.', dir=directory)
    temporary = os.path.join(temporary_dir, 'export.tmp')
    try:
        yield temporary
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
        os.rmdir(temporary_dir)


def izom_propui_free_atomic_write_text(filepath, text):
    with izom_propui_free_atomic_output_path(filepath) as temporary:
        with open(temporary, 'w', encoding='utf-8') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
