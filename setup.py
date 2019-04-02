# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo module for providing access request feature."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.35',
    'coverage>=4.0',
    'invenio-records-ui>=1.0.1',
    'isort>=4.3.4',
    'mock>=1.3.0',
    'pydocstyle>=2.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=2.5.1',
    'pytest-pep8>=1.0.6',
    'pytest>=3.7.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5,<1.6',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'blinker>=1.4',
    'Flask-BabelEx>=0.9.2',
    'Flask-Breadcrumbs>=0.4.0',
    'Flask>=1.0.2',
    'invenio-access>=1.0.0a11',
    'invenio-accounts>=1.0.0b1',
    'invenio-db>=1.0.0b3',
    'invenio-files-rest>=1.0.0a14',
    'invenio-formatter>=1.0.0a2',
    'invenio-i18n>=1.0.0b1',
    'invenio-mail>=1.0.0a5',
    'invenio-pidstore>=1.0.0b1',
    'invenio-records>=1.0.0b1',
    'itsdangerous>=1.1.0',
    'WTForms>=2.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('zenodo_accessrequests', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='zenodo-accessrequests',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='GPLv2',
    author='CERN',
    author_email='info@zenodo.org',
    url='https://github.com/zenodo/zenodo-accessrequests',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_admin.views': [
            'accessrequest_adminview = '
            'zenodo_accessrequests.admin:accessrequest_adminview',
            'secretlinks_adminview = '
            'zenodo_accessrequests.admin:secretlinks_adminview',
        ],
        'invenio_base.apps': [
            'zenodo_accessrequests = '
            'zenodo_accessrequests:ZenodoAccessRequests',
        ],
        'invenio_base.blueprints': [
            'zenodo_accessrequests_requests = '
            'zenodo_accessrequests.views.requests:blueprint',
            'zenodo_accessrequests_settings = '
            'zenodo_accessrequests.views.settings:blueprint',
        ],
        'invenio_db.models': [
            'zenodo_accessrequests = zenodo_accessrequests.models',
        ],
        'invenio_i18n.translations': [
            'messages = zenodo_accessrequests'
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
