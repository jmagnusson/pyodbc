#!/usr/bin/python

import os
import subprocess as subp
import sys

from setuptools import setup
from setuptools.extension import Extension

VERSION = '3.0.8'

def _print(s):
    # Python 2/3 compatibility
    sys.stdout.write(s + '\n')


def main():
    settings = get_compiler_settings()
    files = [os.path.abspath(os.path.join('src', f))
                              for f in os.listdir('src') if f.endswith('.cpp')]
    kwargs = {
    'name': "pyodbc",
    'version': VERSION,
    'description': "DB API Module for ODBC",
    'long_description': ('A Python DB API 2 module for ODBC. This project '
        'provides an up-to-date, '
        'convenient interface to ODBC using native data types like datetime '
        'and decimal.'),
    'maintainer': "Michael Kleehammer",
    'maintainer_email': "michael@kleehammer.com",
    'ext_modules': [Extension('pyodbc', files, **settings)],
    'license': 'MIT',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
    ],
    'url': 'http://code.google.com/p/pyodbc',
    'download_url': 'http://code.google.com/p/pyodbc/downloads/list',
    }

    if sys.hexversion >= 0x02060000:
        kwargs['options'] = {
            'bdist_wininst': {'user_access_control' : 'auto'}
            }

    setup(**kwargs)


def get_compiler_settings():
    settings = {
        'libraries': [],
        'define_macros': [('PYODBC_VERSION', VERSION)]
    }

    # This isn't the best or right way to do this, but I don't see how someone is supposed to sanely subclass the build
    # command.
    for option in ['assert', 'trace', 'leak-check']:
        try:
            sys.argv.remove('--%s' % option)
            settings['define_macros'].append(('PYODBC_%s' % option.replace('-', '_').upper(), 1))
        except ValueError:
            pass

    if os.name == 'nt':
        settings['extra_compile_args'] = [
            '/Wall',
            '/wd4668',
            '/wd4820',
            # Function selected for automatic inline expansion
            '/wd4711',
            # Unreferenced formal parameter
            '/wd4100',
            # "conditional expression is constant" testing compilation
            # constants
            '/wd4127',
            # Casts to PYCFunction which doesn't have the keywords parameter
            '/wd4191',
        ]
        settings['libraries'].append('odbc32')
        settings['libraries'].append('advapi32')

        if '--debug' in sys.argv:
            sys.argv.remove('--debug')
            settings['extra_compile_args'].extend('/Od /Ge /GS /GZ /RTC1 /Wp64 /Yd'.split())

    elif os.environ.get("OS", '').lower().startswith('windows'):
        # Windows Cygwin (posix on windows)
        # OS name not windows, but still on Windows
        settings['libraries'].append('odbc32')

    elif sys.platform == 'darwin':
        IODBC = 'iodbc'
        UNIXODBC = 'odbc.2'
        odbc_lib = IODBC # OS/X ships with iODBC, so default to that lib.

        # Determine if unixODBC is installed and use that instead if available.
        proc = subp.Popen(('gcc', '-l{0}'.format(UNIXODBC)), stderr=subp.PIPE)
        _, stderr = proc.communicate()
        if 'ld: library not found for' not in stderr:
            odbc_lib = UNIXODBC
        settings['libraries'].append(odbc_lib)

        # Python functions take a lot of 'char *' that really should be const.
        # gcc complains about this *a lot*.
        settings['extra_compile_args'] = ['-Wno-write-strings', '-Wno-deprecated-declarations']

        # Apple has decided they won't maintain the iODBC system in OS/X
        # and has added deprecation warnings in 10.8.
        # For now target 10.7 to eliminate the warnings with iODBC.
        if odbc_lib == 'iodbc':
            settings['define_macros'].append( ('MAC_OS_X_VERSION_10_7',) )

    else:
        # Other posix-like: Linux, Solaris, etc.

        # Python functions take a lot of 'char *' that really should be const.  gcc complains about this *a lot*
        settings['extra_compile_args'] = ['-Wno-write-strings']

        # What is the proper way to detect iODBC, MyODBC, unixODBC, etc.?
        settings['libraries'].append('odbc')

    return settings

if __name__ == '__main__':
    main()
