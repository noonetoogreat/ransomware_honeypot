#!/usr/bin/env python

"""
Python functions for finding open files and PIDs that have opened a file.
"""

import numbers
import subprocess
import sys

try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

def get_open_files(*pids):
    """
    Find files opened by specified process ID(s).
    Parameters
    ----------
    pids : list of int
        Process IDs.
    Returns
    -------
    files : list of str
        Open file names.
    """

    for pid in pids:
        if not isinstance(pid, numbers.Integral):
            raise ValueError('invalid PID')
    files = set()
    for pid in pids:
        try:
            out = subprocess.check_output(['lsof', '-wXFn', '+p', str(pid)],
                    stderr=DEVNULL)
        except:
            pass
        else:
            lines = out.strip().split('\n')
            for line in lines:

                # Skip sockets, pipes, etc.:
                if line.startswith('n') and line[1] == '/':
                    files.add(line[1:])
    return list(files)

def get_pids_open(*files):
    """
    Find processes with open handles for the specified file(s).
    Parameters
    ----------
    files : list of str
        File paths.
    Returns
    -------
    pids : list of int
        Process IDs with open handles to the specified files.
    """
    for f in files:
        if not isinstance(f, basestring):
            raise ValueError('invalid file name %s' % f)
    pids = set()
    try:
        out = subprocess.check_output(['lsof', '+wt']+list(files), stderr=DEVNULL)
        print out
    except Exception as e:
        out = str(e.output)
    if not out.strip():
        return []
    lines = out.strip().split('\n')
    for line in lines:
        pids.add(int(line))
    return list(pids)

def main():
    while True:
        print get_pids_open(sys.argv[1])

if __name__ == '__main__':
    main()