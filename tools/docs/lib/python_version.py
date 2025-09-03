#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2017-2025 Mauro Carvalho Chehab <mchehab+huawei@kernel.org>

"""
Handle Python version check logic.

Not all Python versions are supported by scripts. Yet, on some cases,
like during documentation build, a newer version of python could be
available.

This class allows checking if the minimal requirements are followed.

Better than that, PythonVersion.check_python() not only checks the minimal
requirements, but it automatically switches to a the newest available
Python version if present.

"""

import os
import re
import subprocess
import sys

from glob import glob

class PythonVersion:
    """
    Ancillary methods that checks for missing dependencies for different
    types of types, like binaries, python modules, rpm deps, etc.
    """

    def __init__(self, version):
        """Ïnitialize self.version tuple from a version string"""
        self.version = self.parse_version(version)

    @staticmethod
    def parse_version(version):
        """Convert a major.minor.patch version into a tuple"""
        return tuple(int(x) for x in version.split("."))

    @staticmethod
    def ver_str(version):
        """Returns a version tuple as major.minor.patch"""
        return ".".join([str(x) for x in version])

    def __str__(self):
        """Returns a version tuple as major.minor.patch from self.version"""
        return self.ver_str(self.version)

    @staticmethod
    def get_python_version(cmd):
        """
        Get python version from a Python binary. As we need to detect if
        are out there newer python binaries, we can't rely on sys.release here.
        """

        kwargs = {}
        if sys.version_info < (3, 7):
            kwargs['universal_newlines'] = True
        else:
            kwargs['text'] = True

        result = subprocess.run([cmd, "--version"],
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                **kwargs, check=False)

        version = result.stdout.strip()

        match = re.search(r"(\d+\.\d+\.\d+)", version)
        if match:
            return PythonVersion.parse_version(match.group(1))

        print(f"Can't parse version {version}")
        return (0, 0, 0)

    @staticmethod
    def find_python(min_version):
        """
        Detect if are out there any python 3.xy version newer than the
        current one.

        Note: this routine is limited to up to 2 digits for python3. We
        may need to update it one day, hopefully on a distant future.
        """
        patterns = [
            "python3.[0-9]",
            "python3.[0-9][0-9]",
        ]

        # Seek for a python binary newer than min_version
        for path in os.getenv("PATH", "").split(":"):
            for pattern in patterns:
                for cmd in glob(os.path.join(path, pattern)):
                    if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
                        version = PythonVersion.get_python_version(cmd)
                        if version >= min_version:
                            return cmd

        return None

    @staticmethod
    def check_python(min_version):
        """
        Check if the current python binary satisfies our minimal requirement
        for Sphinx build. If not, re-run with a newer version if found.
        """
        cur_ver = sys.version_info[:3]
        if cur_ver >= min_version:
            ver = PythonVersion.ver_str(cur_ver)
            return

        python_ver = PythonVersion.ver_str(cur_ver)

        new_python_cmd = PythonVersion.find_python(min_version)
        if not new_python_cmd:
            print(f"ERROR: Python version {python_ver} is not spported anymore\n")
            print("       Can't find a new version. This script may fail")
            return

        # Restart script using the newer version
        script_path = os.path.abspath(sys.argv[0])
        args = [new_python_cmd, script_path] + sys.argv[1:]

        print(f"Python {python_ver} not supported. Changing to {new_python_cmd}")

        try:
            os.execv(new_python_cmd, args)
        except OSError as e:
            sys.exit(f"Failed to restart with {new_python_cmd}: {e}")
