# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Base test case for access requests."""

from __future__ import absolute_import, print_function

from flask import current_app

from zenodo_accessrequests.models import AccessRequest


def create_access_request(pid_value, users, confirmed):
    """Access Request."""
    datastore = current_app.extensions['security'].datastore
    receiver = datastore.get_user(users['receiver']['id'])
    sender = datastore.get_user(users['sender']['id'])
    return AccessRequest.create(
        recid=pid_value,
        receiver=receiver,
        sender_full_name="Another Name",
        sender_email="anotheremail@example.org",
        sender=sender if confirmed else None,
        justification="Bla bla bla",
    )
