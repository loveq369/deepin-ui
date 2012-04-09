#! /usr/bin/env python

from setuptools import setup, Extension
import os
import commands

def list_files(target_dir, install_dir):
    '''List files for option `data_files`.'''
    results = []
    for root, dirs, files in os.walk(target_dir):
        for filepath in files:
            data_dir = os.path.dirname(os.path.join(root, filepath))
            data_file = os.path.join(root, filepath)
            results.append((data_dir, [data_file]))
            print results
    return results                

def pkg_config_cflags(pkgs):
    '''List all include paths that output by `pkg-config --cflags pkgs`'''
    return map(lambda path: path[2::], commands.getoutput('pkg-config --cflags-only-I %s' % (' '.join(pkgs))).split())

cairo_mod = Extension('dtk_cairo_blur',
                include_dirs = pkg_config_cflags(['cairo']),
                libraries = ['cairo', 'pthread', 'glib-2.0'],
                sources = ['./dtk/ui/cairo_blur.c'])

browser_mod = Extension('dtk_browser',
                include_dirs = pkg_config_cflags(['gtk+-2.0', 'webkit-1.0', 'pygobject-2.0']),
                libraries = ['webkitgtk-1.0', 'pthread', 'glib-2.0'],
                sources = ['./dtk/ui/browser.c'])

setup(name='dtk',
      version='0.1',
      ext_modules = [cairo_mod, browser_mod],
      description='UI toolkit for Linux Deepin.',
      long_description ="""UI toolkit for Linux Deepin.""",
      author='Linux Deepin Team',
      author_email='wangyong@linuxdeepin.com',
      license='GPL-3',
      url="https://github.com/manateelazycat/deepin-ui-toolkit",
      download_url="git://github.com/manateelazycat/deepin-ui-toolkit.git",
      platforms = ['Linux'],
      packages = ['dtk', 'dtk.ui'],
      data_files = list_files("dtk/theme","dtk/theme"),
      )

