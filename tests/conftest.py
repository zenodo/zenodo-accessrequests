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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import uuid
from datetime import datetime

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_menu import Menu as FlaskMenu
from helpers import create_access_request
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_accounts.testutils import create_test_user
from invenio_accounts.views import blueprint as blueprint_user
from invenio_db import db as db_
from invenio_db import InvenioDB
from invenio_formatter import InvenioFormatter
from invenio_mail import InvenioMail as Mail
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import InvenioRecords
from invenio_records.api import Record
from invenio_records_ui import InvenioRecordsUI
from simplekv.memory.redisstore import RedisStore
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from zenodo_accessrequests import ZenodoAccessRequests
from zenodo_accessrequests.views.requests import blueprint as request_blueprint
from zenodo_accessrequests.views.settings import \
    blueprint as settings_blueprint


@pytest.yield_fixture
def app(request):
    """Flask application fixture."""
    app_ = Flask('testapp')
    app_.config.update(
        TESTING=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_RESULT_BACKEND="cache",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'
        ),
        SECRET_KEY='mysecret',
        SUPPORT_EMAIL='info@zenodo.org',
        WTF_CSRF_ENABLED=False,
        SERVER_NAME='test.it',
        RECORDS_UI_ENDPOINTS=dict(
            recid=dict(
                pid_type='recid',
                route='/records/<pid_value>',
                template='invenio_records_ui/detail.html',
            ),
            recid_access_request=dict(
                pid_type='recid',
                route='/records/<pid_value>/accessrequest',
                template='zenodo_accessrequests/access_request.html',
                view_imp='zenodo_accessrequests.views.requests.access_request',
                methods=['GET', 'POST'],
            ),
            recid_access_request_email_confirm=dict(
                pid_type='recid',
                route='/records/<pid_value>/accessrequest/<token>/confirm',
                #  template='invenio_records_ui/detail.html',
                view_imp='zenodo_accessrequests.views.requests.confirm',
            ),
        ),
    )

    InvenioFormatter(app_)
    Babel(app_)
    InvenioDB(app_)
    InvenioAccounts(app_)
    InvenioRecords(app_)
    FlaskMenu(app_)
    Mail(app_)
    InvenioRecordsUI(app_)
    InvenioAccess(app_)
    ZenodoAccessRequests(app_)
    InvenioPIDStore(app_)

    app_.register_blueprint(request_blueprint)
    app_.register_blueprint(settings_blueprint)
    app_.register_blueprint(blueprint_user)

    with app_.app_context():
        yield app_


@pytest.yield_fixture
def db(app, request):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()

    yield db_

    drop_database(str(db_.engine.url))
    # Delete sessions in kvsession store
    if hasattr(app, 'kvsession_store') and \
            isinstance(app.kvsession_store, RedisStore):
        app.kvsession_store.redis.flushall()


@pytest.fixture
def users(app, db):
    """Demo users."""
    sender = create_test_user(
        email='sender@myemail.it',
        password='sender',
        confirmed_at=datetime.utcnow(),
    )
    receiver = create_test_user(
        email='receiver@myemail.it',
        password='receiver',
    )

    users = {
        "sender": dict(id=sender.id),
        "receiver": dict(id=receiver.id),
    }

    return users


@pytest.fixture
def access_request_confirmed(app, db, users, record_example):
    """Access Request."""
    pid_value, record = record_example
    with db.session.begin_nested():
        id_req = create_access_request(pid_value, users, confirmed=True).id
    db.session.commit()
    return id_req


@pytest.fixture
def access_request_not_confirmed(app, db, users, record_example):
    """Access Request."""
    pid_value, record = record_example
    with db.session.begin_nested():
        id_req = create_access_request(
            pid_value, users, confirmed=False).id
    db.session.commit()
    return id_req


@pytest.fixture
def record_example(app, db, users):
    """Create an example of record."""
    with db.session.begin_nested():
        rec_uuid = uuid.uuid4()
        pid = PersistentIdentifier.create(
            'recid', '1', object_type='rec', object_uuid=rec_uuid,
            status=PIDStatus.REGISTERED)
        record = Record.create({
            'title': 'Registered',
            'description': 'This is an awesome description',
            'control_number': '1',
            'access_right': 'restricted',
            'access_conditions': 'fuu',
            'owners': [users['receiver']['id']],
            'recid': 1,
        }, id_=rec_uuid)
    db.session.commit()
    result = pid.pid_value, dict(record)
    return result
