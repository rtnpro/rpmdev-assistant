# -*- coding: utf-8 -*-
from __future__ import absolute_import
from subprocess import Popen, PIPE
from collections import OrderedDict
import re


def execute(cmd):
    print 'Executing: %s' % cmd
    print '=' * 80
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out


def get_deps(package_name, disablerepos=[], enablerepos=[],
             build=True):
    """
    Get a list of dependencies for a package in specified repositories.

    Args:
        package_name: A string for the name of the package.
        disablerepos: A list of disabled repository names.
        enablerepos: A list of enabled repository names.
        build: A boolean, by default True. If True, build dependencies
            for the package are also searched, else, only runtime
            dependencies are searched.

    Returns:
        A set of dependencies for the given package.
    """
    package_names = [package_name]
    if build:
        package_names.append(package_name + '.src')
    cmd = "repoquery --quiet"
    if disablerepos:
        cmd += " %s" % " ".join(
            ["--disablerepo=%s" % repo for repo in disablerepos])
    if enablerepos:
        cmd += " %s" % " ".join(
            ["--enablerepo=%s" % repo for repo in enablerepos])
    cmd += " --requires --resolve %s" % " ".join(package_names)
    output = execute(cmd)
    deps = set()
    for line in output.splitlines():
        if line.strip():
            deps.add(re.sub('-\d+$', '', line.split(':')[0]))
    return deps


def resolve_packages(package_names, disablerepos=[], enablerepos=[]):
    """
    Resolve a list of package names in specified repositories.

    Args:
        package_names: An iterable object: list, set, etc. for package names.
        disablerepos: A list of disabled repository names.
        enablerepos: A list of enabled repository names.

    Returns:
        A set of resolved dependencies for the given package names.
    """
    if not package_names:
        return set()
    cmd = "repoquery --quiet"
    if disablerepos:
        cmd += " %s" % " ".join(
            ["--disablerepo=%s" % repo for repo in disablerepos])
    if enablerepos:
        cmd += " %s" % " ".join(
            ["--enablerepo=%s" % repo for repo in enablerepos])
    cmd += " --resolve %s" % " ".join(package_names)
    output = execute(cmd)
    packages = set()
    for line in output.splitlines():
        if line.strip():
            packages.add(re.sub('-\d+$', '', line.split(':')[0]))
    return packages


def get_missing_deps(
        package_name,
        source_enablerepos=[],
        source_disablerepos=[],
        target_enablerepos=[],
        target_disablerepos=[],
        build=True):
    """
    Get missing RPM dependecies for a package in one or many
    target repositories from one or many source repositories.

    Valid repository names are the ones accepted by --enablerepo
    and --disablerepo arguments of repoquery command.
    For example, 'fedora*', 'fedora-base', 'fedora-updates',
    'centos*', etc.

    Args:
        package_name: A string for the package name whose missing
            dependencies need to found.
        source_enablerepos: A list of source repositories to enable.
        source_disabledrepos: A list of source repositories to disable.
        target_enablerepos: A list of target repositories to enable.
        target_disablerepos: A list of target repositories to disable.
        build: A boolean, by default True. If True, we search for
            dependencies required for building the package, else,
            we search only for run time dependencies.

    Returns:
        An OrderedDict representing a graph for all the missing
        dependencies.
    """
    deps_graph = OrderedDict()
    deps_graph[package_name] = set()
    for package, deps in deps_graph.iteritems():
        if deps:
            continue
        source_deps = get_deps(
            package, source_disablerepos, source_enablerepos,
            build=build)
        target_deps_resolved = resolve_packages(
            source_deps, target_disablerepos, target_enablerepos)
        missing_deps = source_deps.difference(target_deps_resolved)
        for missing_dep in missing_deps:
            if missing_dep not in deps_graph:
                deps_graph[missing_dep] = []
        deps_graph[package] = list(missing_deps)
    return deps_graph


def download_src_rpms(package_names):
    print "Downloading Source RPMS"
    execute(
        'yumdownloader --source {package_names} '
        '--destdir=~/rpmbuild/SRPMS/'.format(
            package_names=' '.join(package_names))
    )


def extract_src_rpms():
    print "Extracting source rpms"
    execute(
        'cd ~/rpmbuild/SRPMS; rpm -ivh *.src.rpm')

