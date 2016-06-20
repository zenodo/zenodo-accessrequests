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

"""Model tests."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import pytest
from flask import current_app
from helpers import create_access_request
from mock import Mock

from zenodo_accessrequests.errors import InvalidRequestStateError
from zenodo_accessrequests.models import AccessRequest, RequestStatus, \
    SecretLink
from zenodo_accessrequests.signals import link_created, link_revoked, \
    request_accepted, request_confirmed, request_created, request_rejected


def test_create_nouser(app, db, users, record_example):
    """Test access request creation without user."""
    mock_request_created = Mock()
    mock_request_confirmed = Mock()
    pid_value, record = record_example

    with app.test_request_context():
        with request_created.connected_to(mock_request_created):
            with request_confirmed.connected_to(mock_request_confirmed):
                datastore = current_app.extensions['security'].datastore
                receiver = datastore.get_user(users['receiver']['id'])

                r = AccessRequest.create(
                    recid=pid_value,
                    receiver=receiver,
                    sender_full_name="John Smith",
                    sender_email="info@invenio-software.org",
                    justification="Bla bla bla",
                )

                assert r.status == RequestStatus.EMAIL_VALIDATION
                assert r.sender_user_id is None
                assert r.created is not None
                assert r.modified is not None
                assert r.message == u''

                assert mock_request_created.called
                assert not mock_request_confirmed.called


def test_create_withuser(app, db, users, record_example):
    """Test access request creation with user."""
    mock_request_created = Mock()
    mock_request_confirmed = Mock()
    pid_value, record = record_example

    with app.test_request_context():
        with request_created.connected_to(mock_request_created):
            with request_confirmed.connected_to(mock_request_confirmed):
                datastore = current_app.extensions['security'].datastore
                receiver = datastore.get_user(users['receiver']['id'])
                sender = datastore.get_user(users['sender']['id'])

                r = AccessRequest.create(
                    recid=pid_value,
                    receiver=receiver,
                    sender_full_name="Another Name",
                    sender_email="anotheremail@example.org",
                    sender=sender,
                    justification="Bla bla bla",
                )

                assert r.status == RequestStatus.PENDING
                assert r.sender_user_id == sender.id
                assert r.created is not None
                assert r.modified is not None
                assert r.message == u''
                assert r.sender_full_name == u'Another Name'
                assert r.sender_email == u'anotheremail@example.org'

                assert not mock_request_created.called
                assert mock_request_confirmed.called


def test_accept(app, db, users, record_example, access_request_not_confirmed,
                access_request_confirmed):
    """Test accept signal and state."""
    mock_request_accepted = Mock()

    with app.test_request_context():
        with request_accepted.connected_to(mock_request_accepted):

            # Invalid operation when email not confirmed
            r = AccessRequest.query.filter_by(
                id=access_request_not_confirmed).first()
            with pytest.raises(InvalidRequestStateError):
                r.accept()
            assert not mock_request_accepted.called

            # Test signal and state
            r = AccessRequest.query.filter_by(
                id=access_request_confirmed).first()
            r.accept()
            assert r.status == RequestStatus.ACCEPTED
            assert mock_request_accepted.called
            assert mock_request_accepted.call_args[0][0] == r

            # Invalid operation for accepted request
            with pytest.raises(InvalidRequestStateError):
                r.confirm_email()


def test_reject(app, db, users, record_example, access_request_not_confirmed,
                access_request_confirmed):
    """Test reject signal and state."""
    mock_request_rejected = Mock()

    with app.test_request_context():
        with request_rejected.connected_to(mock_request_rejected):

            r = AccessRequest.query.filter_by(
                id=access_request_not_confirmed).first()
            with pytest.raises(InvalidRequestStateError):
                r.reject()
            assert not mock_request_rejected.called

            r = AccessRequest.query.filter_by(
                id=access_request_confirmed).first()
            r.reject()
            assert r.status == RequestStatus.REJECTED
            assert mock_request_rejected.call_args[0][0] == r

            with pytest.raises(InvalidRequestStateError):
                r.confirm_email()


def test_confirm_email(app, db, users, record_example,
                       access_request_not_confirmed):
    """Test confirm email signal and state."""
    mock_request_confirmed = Mock()
    pid_value, record = record_example

    with app.test_request_context():
        with request_confirmed.connected_to(mock_request_confirmed):

            r = AccessRequest.query.filter_by(
                id=access_request_not_confirmed).first()
            r.confirm_email()
            assert r.status == RequestStatus.PENDING
            assert mock_request_confirmed.call_args[0][0] == r


def test_query_by_receiver(app, db, users, record_example):
    """Test query by receiver."""
    pid_value, record = record_example

    with app.test_request_context():
        datastore = current_app.extensions['security'].datastore
        receiver = datastore.get_user(users['receiver']['id'])
        sender = datastore.get_user(users['sender']['id'])

        assert AccessRequest.query_by_receiver(receiver).count() == 0
        assert AccessRequest.query_by_receiver(sender).count() == 0

        # Create an accesrequest
        r = create_access_request(pid_value=pid_value, users=users,
                                  confirmed=False)

        assert AccessRequest.query_by_receiver(receiver).count() == 1
        assert AccessRequest.query_by_receiver(sender).count() == 0

        assert AccessRequest.get_by_receiver(r.id, receiver) is not None
        assert AccessRequest.get_by_receiver(r.id, sender) is None


def test_create_secret_link(app, db, users, record_example):
    """Test creation of secret link via token."""
    pid_value, record = record_example

    with app.test_request_context():
        datastore = current_app.extensions['security'].datastore
        receiver = datastore.get_user(users['receiver']['id'])

        r = create_access_request(pid_value=pid_value, users=users,
                                  confirmed=False)
        l = r.create_secret_link(
            "My link", "Link description",
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        assert r.link == l
        assert l.title == "My link"
        assert l.description == "Link description"
        assert l.extra_data == dict(recid=pid_value)
        assert l.owner == receiver


def test_creation(app, db, users, record_example):
    """Test link creation."""
    mock_link_created = Mock()
    pid_value, record = record_example

    with app.test_request_context():
        with link_created.connected_to(mock_link_created):
            datastore = current_app.extensions['security'].datastore
            receiver = datastore.get_user(users['receiver']['id'])

            l = SecretLink.create("Test title", receiver,
                                  dict(recid=pid_value),
                                  description="Test description")

            assert l.title == "Test title"
            assert l.description == "Test description"
            assert l.expires_at is None
            assert l.token != ''
            assert mock_link_created.called
            db.session.commit()

            l = SecretLink.query.get(l.id)
            assert SecretLink.validate_token(l.token, dict(recid=pid_value),)
            assert not SecretLink.validate_token(l.token, dict(recid='-1'))


def test_revoked(app, db, users):
    """Test link revocation."""
    mock_link_revoked = Mock()

    with app.test_request_context():
        with link_revoked.connected_to(mock_link_revoked):
            datastore = current_app.extensions['security'].datastore
            receiver = datastore.get_user(users['receiver']['id'])

            l = SecretLink.create(
                "Test title", receiver, dict(recid='123456'),
                description="Test description"
            )
            assert not l.is_revoked()
            assert l.is_valid()
            l.revoke()
            assert l.is_revoked()
            assert not l.is_valid()

            assert mock_link_revoked.called
            assert l.revoke() is False


def test_expired(app, db, users):
    """Test link expiry date."""
    with app.test_request_context():
        datastore = current_app.extensions['security'].datastore
        receiver = datastore.get_user(users['receiver']['id'])

        l = SecretLink.create(
            "Test title", receiver, dict(recid='123456'),
            description="Test description",
            expires_at=datetime.utcnow() - timedelta(days=1))
        assert l.is_expired()
        assert not l.is_valid()

        l = SecretLink.create(
            "Test title", receiver, dict(recid='123456'),
            description="Test description",
            expires_at=datetime.utcnow() + timedelta(days=1))
        assert not l.is_expired()
        assert l.is_valid()


def test_query_by_owner(app, db, users):
    """Test query by owner."""
    with app.test_request_context():
        datastore = current_app.extensions['security'].datastore
        receiver = datastore.get_user(users['receiver']['id'])
        sender = datastore.get_user(users['sender']['id'])

        assert SecretLink.query_by_owner(receiver).count() == 0
        assert SecretLink.query_by_owner(sender).count() == 0

        SecretLink.create("Testing", receiver, dict(recid='1'))

        assert SecretLink.query_by_owner(receiver).count() == 1
        assert SecretLink.query_by_owner(sender).count() == 0


def test_get_absolute_url(app, db, users):
    """Test absolute url."""
    with app.test_request_context():
        datastore = current_app.extensions['security'].datastore
        receiver = datastore.get_user(users['receiver']['id'])

        l = SecretLink.create("Testing", receiver, dict(recid='1'))
        url = l.get_absolute_url('invenio_records_ui.recid')
        assert "/records/1?" in url
        assert "token={0}".format(l.token) in url
