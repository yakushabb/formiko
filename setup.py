#!/usr/bin/env python

from setuptools import setup
from docutils.core import publish_string
from docutils.writers.manpage import Writer

from io import open
from gzip import open as zopen
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_data import install_data
from distutils import log
from os import path, makedirs, listdir
from shutil import rmtree

from formiko import __version__, __url__, __comment__


def doc():
    with open("README.rst", "r", encoding="utf-8") as readme:
        return readme.read().strip()


def icons_data():
    path = 'share/icons/hicolor'
    icons = [("%s/scalable/apps" % path, ["icons/formiko.svg"])]
    for size in (16, 22, 24, 32, 48, 64, 128, 256, 512):
        icons.append(("%s/%dx%d/apps" % (path, size, size),
                     ["icons/%dx%d/formiko.png" % (size, size)]))
    return icons


def man_page(writer, src, dst):
    with open(src, encoding="utf-8") as source:
        rst = source.read()
    with zopen(dst, 'wb') as destination:
        destination.write(publish_string(source=rst, writer=writer))


class XBuild(build):
    def initialize_options(self):
        build.initialize_options(self)
        self.man_base = None

    def finalize_options(self):
        build.finalize_options(self)
        if self.man_base is None:
            self.man_base = path.join(self.build_base, 'man')

    def run(self):
        build.run(self)
        log.info("building man pages")
        if self.dry_run:
            return

        writer = Writer()
        if not path.exists(self.man_base):
            makedirs(self.man_base)
        for page in ('formiko', 'formiko-vim'):
            man_page(writer, page+'.rst', '%s/%s.1.gz' % (self.man_base, page))


class XClean(clean):
    def initialize_options(self):
        clean.initialize_options(self)
        self.man_base = None

    def finalize_options(self):
        clean.finalize_options(self)
        if self.man_base is None:
            self.man_base = path.join(self.build_base, 'man')

    def run(self):
        clean.run(self)
        log.info("clean man pages")
        if self.dry_run:
            return

        if path.exists(self.man_base):
            rmtree(self.man_base)


class XInstallData(install_data):
    def initialize_options(self):
        install_data.initialize_options(self)
        self.man_base = None
        self.build_base = None

    def finalize_options(self):
        install_data.finalize_options(self)
        self.set_undefined_options('build', ('build_base', 'build_base'))
        if self.man_base is None:
            self.man_base = path.join(self.build_base, 'man')

    def run(self):
        self.data_files.append(
            ('share/man/man1',
             list("%s/%s" % (self.man_base, page)
                  for page in listdir(self.man_base))))
        install_data.run(self)


setup(
    name="formiko",
    version=__version__,
    description=__comment__,
    author="Ondrej Tuma",
    author_email="mcbig@zeropage.cz",
    url=__url__,
    packages=['formiko'],
    data_files=[('share/doc/formiko', ['README.rst', 'COPYING', 'ChangeLog',
                                       'AUTHORS']),
                ("share/applications", ["formiko.desktop",
                                        "formiko-vim.desktop"]),
                ('share/formiko/icons', ['icons/formiko.svg'])] + icons_data(),
    keywords=["doc", "html", "rst", "docutils", "md", "markdown", "editor"],
    license="BSD",
    long_description=doc(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Editors :: Documentation",
        "Topic :: Text Editors :: Text Processing",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities"],
    requires=['docutils (>= 0.12)', 'python_gi', 'webkit2', 'gtksourceview'],
    install_requires=['docutils >= 0.12'],
    entry_points={
        'gui_scripts': [
            'formiko = formiko.main:main',
            'formiko-vim = formiko.main:main_vim'
        ]
    },
    cmdclass={'build': XBuild, 'clean': XClean, 'install_data': XInstallData}
)
