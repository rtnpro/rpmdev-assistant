rpmdev-assistant
================

An assistant for RPM packaging


Usage
#####

1. Create ``*.repo`` files in ``/etc/yum.repos.d/`` as needed.
2. Change directory to ``./rpmdev_assistant``
3. Open a python shell and something as below:

``` python
import lib
missing_deps_data = lib.get_missing_deps(
    'mesos', source_enablerepos=['fedora-source'],
    source_disablerepos=[],
    target_enablerepos=['centos*', 'epel*'],
    target_disablerepos=['*'])
print missing_deps_data
```
