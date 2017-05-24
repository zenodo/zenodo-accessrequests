# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Utils."""

from __future__ import absolute_import, print_function

from functools import partial
from flask import current_app

from invenio_db.utils import rebuild_encrypted_properties
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from .models import SecretLink

resolver = Resolver(pid_type='recid', object_type='rec',
                    getter=partial(Record.get_record, with_deleted=True))
"""Get a record resolver."""


def get_record(recid):
    """Get record."""
    return resolver.resolve(str(recid))


def rebuild_secret_link_tokens(old_key):
    """Rebuild the token field in SecretLink when the SECRET_KEY is changed."""
    current_app.logger.info('rebuilding SecretLink.token...')
    rebuild_encrypted_properties(old_key, SecretLink, ['token'])
