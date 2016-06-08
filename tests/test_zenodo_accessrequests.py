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


"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask, session, url_for
from mock import patch

from zenodo_accessrequests import ZenodoAccessRequests
from zenodo_accessrequests.models import SecretLink


def test_version():
    """Test version import."""
    from zenodo_accessrequests import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = ZenodoAccessRequests(app)
    assert 'zenodo-accessrequests' in app.extensions

    app = Flask('testapp')
    ext = ZenodoAccessRequests()
    assert 'zenodo-accessrequests' not in app.extensions
    ext.init_app(app)
    assert 'zenodo-accessrequests' in app.extensions


def test_view(app, db, users, record_example):
    """Test view."""
    pid_value, record = record_example
    with app.test_client() as client:
        res = client.get(url_for(
            'invenio_records_ui.recid_access_request', pid_value=pid_value))
        assert res.status_code == 200


def test_token_are_saved_in_session(app, db, users, record_example):
    """Test view."""
    pid_value, record = record_example
    with app.test_client() as client:
        with patch.object(SecretLink,
                          'validate_token', return_value=True):
            client.get("/", query_string=dict(token='123'))
            assert session['accessrequests-secret-token'] == '123'
