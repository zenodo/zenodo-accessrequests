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

"""Test signal receivers."""

from __future__ import absolute_import, print_function

import pytest
from helpers import create_access_request
from invenio_pidstore.errors import PIDDoesNotExistError
from mock import patch

from zenodo_accessrequests.models import AccessRequest
from zenodo_accessrequests.receivers import _send_notification, \
    create_secret_link


def test_send_notification(app, db):
    """Test sending of notifications."""
    with app.test_request_context():
        with patch('invenio_mail.tasks.send_email.delay') as mock:
            _send_notification(
                "info@invenio-software.org",
                "Test subject",
                "zenodo_accessrequests/emails/accepted.tpl",
                var1="value1",
            )
            assert mock.called
            msg = mock.call_args[0][0]
            assert msg['recipients'] == ["info@invenio-software.org"]
            assert msg['sender'] == 'info@zenodo.org'
            assert msg['subject'] == 'Test subject'


def test_create_secret_link(app, db, users, record_example,
                            access_request_confirmed):
    """Test creation of secret link."""
    with app.test_request_context():
        r = AccessRequest.query.filter_by(id=access_request_confirmed).first()
        create_secret_link(r)

        assert r.link.title == "Registered"
        assert "anotheremail@example.org" in r.link.description
        assert "Another Name" in r.link.description
        assert "Bla bla bla" in r.link.description


def test_create_secret_link_norecord(app, db, users):
    """Test creation of secret link with no record."""
    # Patch get_record
    with app.test_request_context():
        with patch('zenodo_accessrequests.utils.get_record',
                   return_value=None):
            with pytest.raises(PIDDoesNotExistError):
                r = create_access_request("1", users, confirmed=True)
