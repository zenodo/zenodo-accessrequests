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

"""Token creation and validation test case."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import pytest
from itsdangerous import BadData, BadSignature, JSONWebSignatureSerializer, \
    SignatureExpired

from zenodo_accessrequests.tokens import EmailConfirmationSerializer, \
    EncryptedTokenMixIn, SecretLinkFactory, SecretLinkSerializer, \
    TimedSecretLinkSerializer


def test_email_confirmation_serializer_create_validate(app, db):
    """Test token creation."""
    extra_data = dict(email="info@invenio-software.org")
    with app.app_context():
        s = EmailConfirmationSerializer()
        t = s.create_token(1, extra_data)
        data = s.validate_token(t, expected_data=extra_data)
        assert data['id'] == 1
        assert data['data'] == extra_data


def test_email_confirmation_serializer_expired(app, db):
    """Test token expiry."""
    extra_data = dict(email="info@invenio-software.org")
    with app.app_context():
        s = EmailConfirmationSerializer(expires_in=-20)
        t = s.create_token(1, extra_data)
        assert s.validate_token(t) is None
        assert s.validate_token(t, expected_data=extra_data) is None
        with pytest.raises(SignatureExpired):
            s.load_token(t)
        assert s.load_token(t, force=True) is not None


def test_email_confirmation_serializer_expected_data_mismatch(app, db):
    """Test token validation."""
    extra_data = dict(email="info@invenio-software.org")
    with app.app_context():
        s = EmailConfirmationSerializer()
        t = s.create_token(1, extra_data)
        assert s.validate_token(t) is not None
        assert s.validate_token(t, dict(notvalid=1)) is None
        assert s.validate_token(t, dict(email='another@email')) is None


def test_email_confirmation_serializer_creation(app, db):
    """Ensure that no two tokens are identical."""
    extra_data = dict(email="info@invenio-software.org")
    with app.app_context():
        s = EmailConfirmationSerializer()
        t1 = s.create_token(1, extra_data)
        t2 = s.create_token(1, extra_data)
        assert t1 != t2


def test_secretlink_serializer_create_validate(app, db):
    """Test token creation."""
    with app.app_context():
        s = SecretLinkSerializer()
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t)
        assert data['id'] == 1234
        assert data['data']['recid'] == 56789


def test_secretlink_serializer_creation(app, db):
    """Ensure that no two tokens are identical."""
    with app.app_context():
        s = SecretLinkSerializer()
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        assert t1 != t2


def test_secretlink_serializer_noencryption(app, db):
    """Test that token is not encrypted."""
    with app.app_context():
        s = SecretLinkSerializer()
        t1 = s.create_token(1, dict(recid=1))
        with pytest.raises(BadSignature):
            JSONWebSignatureSerializer('anotherkey').loads(t1)


class TestSerializer(EncryptedTokenMixIn, SecretLinkSerializer):
    """Test serializer."""
    pass


def test_encryptedtoken_mixin_create_validate(app, db):
    """Test token creation."""
    with app.app_context():
        s = TestSerializer()
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t)
        assert data['id'] == 1234
        assert data['data']['recid'] == 56789


def test_encryptedtoken_mixin_creation(app, db):
    """Ensure that no two tokens are identical."""
    with app.app_context():
        s = TestSerializer()
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        assert t1 != t2


def test_encryptedtoken_mixin_encryption(app, db):
    """Test that token is not encrypted."""
    with app.app_context():
        s = TestSerializer()
        t1 = s.create_token(1, dict(recid=1))
        with pytest.raises(BadData):
            JSONWebSignatureSerializer('anotherkey').loads(t1)


def test_timed_secretlink_serializer_create_validate(app, db):
    """Test token creation."""
    with app.app_context():
        s = TimedSecretLinkSerializer(
            expires_at=datetime.utcnow()+timedelta(days=1))
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t, expected_data=dict(recid=56789))
        assert data['id'] == 1234
        assert data['data']['recid'] == 56789
        assert s.validate_token(t, expected_data=dict(recid=1)) is None


def test_timed_secretlink_serializer_expired(app, db):
    """Test token expiry."""
    with app.app_context():
        s = TimedSecretLinkSerializer(
            expires_at=datetime.utcnow()-timedelta(seconds=20))
        t = s.create_token(1, dict(recid=1))
        assert s.validate_token(t) is None
        assert s.validate_token(t, expected_data=dict(recid=1)) is None
        with pytest.raises(SignatureExpired):
            s.load_token(t)
        assert s.load_token(t, force=True) is not None


def test_timed_secretlink_serializer_creation(app, db):
    """Ensure that no two tokens are identical."""
    with app.app_context():
        s = TimedSecretLinkSerializer(
            expires_at=datetime.utcnow()+timedelta(days=1))
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        assert t1 != t2


def test_secretlink_factory_validation(app, db):
    """Test token validation."""
    extra_data = dict(recid='1')
    with app.app_context():
        t = SecretLinkFactory.create_token(1, extra_data)
        assert SecretLinkFactory.validate_token(
            t, expected_data=extra_data) is not None

        t = SecretLinkFactory.create_token(
            1, extra_data, expires_at=datetime.utcnow()+timedelta(days=1)
        )
        assert SecretLinkFactory.validate_token(
            t, expected_data=extra_data) is not None
        assert SecretLinkFactory.validate_token(
            t, expected_data=dict(recid=2)) is None


def test_secretlink_factory_creation(app, db):
    """Test token creation."""
    extra_data = dict(recid='1')
    with app.app_context():
        d = datetime.utcnow()+timedelta(days=1)

        t = SecretLinkFactory.create_token(1, extra_data)

        assert SecretLinkSerializer().validate_token(
            t, expected_data=extra_data) is not None
        assert TimedSecretLinkSerializer().validate_token(
            t, expected_data=extra_data) is None

        t1 = SecretLinkFactory.create_token(
            1, extra_data, expires_at=d
        )
        t2 = SecretLinkFactory.create_token(1, extra_data)

        assert SecretLinkSerializer().validate_token(
            t1, expected_data=extra_data) is None
        assert TimedSecretLinkSerializer().validate_token(
            t1, expected_data=extra_data) is not None
        assert t1 != t2


def test_secretlink_factory_load_token(app, db):
    """Test token loading."""
    extra_data = dict(recid='1')
    with app.app_context():
        t = SecretLinkFactory.create_token(1, extra_data)
        assert SecretLinkFactory.load_token(t) is not None

        t = SecretLinkFactory.create_token(
            1, extra_data, expires_at=datetime.utcnow()-timedelta(days=1))
        with pytest.raises(SignatureExpired):
            SecretLinkFactory.load_token(t)
        assert SecretLinkFactory.load_token(t, force=True) is not None
