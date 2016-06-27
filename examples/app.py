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


"""Minimal Flask application example for development.

Run example development server:

.. code-block:: console

   $ cd examples
   $ python app.py
"""

from __future__ import absolute_import, print_function

import os
from time import sleep

from flask import Flask
from flask_menu import Menu as FlaskMenu
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_accounts.testutils import create_test_user
from invenio_accounts.views import blueprint as blueprint_user
from invenio_admin import InvenioAdmin
from invenio_db import InvenioDB, db
from invenio_i18n import InvenioI18N
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_mail import InvenioMail as Mail
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_ui import InvenioRecordsUI
from invenio_search import InvenioSearch
from invenio_userprofiles import InvenioUserProfiles
from invenio_userprofiles.views import \
    blueprint_ui_init as userprofiles_blueprint_ui_init

from zenodo_accessrequests import ZenodoAccessRequests
from zenodo_accessrequests.views.requests import blueprint as request_blueprint
from zenodo_accessrequests.views.settings import \
    blueprint as settings_blueprint

# Create Flask application
app = Flask(__name__)

app.config.update(
    #  DEBUG=True,
    CELERY_ALWAYS_EAGER=True,
    CELERY_CACHE_BACKEND="memory",
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    CELERY_RESULT_BACKEND="cache",
    MAIL_SUPPRESS_SEND=True,
    TESTING=True,
    SECRET_KEY='TEST',
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db'
    ),
    SECURITY_PASSWORD_SALT='security-password-salt',
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
    )
)

InvenioDB(app)
InvenioAccounts(app)
InvenioUserProfiles(app)
InvenioRecords(app)
InvenioI18N(app)
FlaskMenu(app)
Mail(app)
InvenioRecordsUI(app)
ZenodoAccessRequests(app)
InvenioPIDStore(app)
InvenioIndexer(app)
InvenioSearch(app)
InvenioAccess(app)
InvenioAdmin(app, permission_factory=lambda x: x,
             view_class_factory=lambda x: x)

app.register_blueprint(request_blueprint)
app.register_blueprint(settings_blueprint)
app.register_blueprint(blueprint_user)
app.register_blueprint(userprofiles_blueprint_ui_init)


@app.cli.group()
def fixtures():
    """Command for working with test data."""


@fixtures.command()
def records():
    """Load test data fixture."""
    import uuid
    from invenio_records.api import Record
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus

    create_test_user()

    indexer = RecordIndexer()

    # Record 1 - Live record
    with db.session.begin_nested():
        rec_uuid = uuid.uuid4()
        pid1 = PersistentIdentifier.create(
            'recid', '1', object_type='rec', object_uuid=rec_uuid,
            status=PIDStatus.REGISTERED)
        Record.create({
            'title': 'Registered',
            'description': 'This is an awesome description',
            'control_number': '1',
            'access_right': 'restricted',
            'access_conditions': 'fuu',
            'owners': [1, 2],
            'recid': 1
        }, id_=rec_uuid)
        indexer.index_by_id(pid1.object_uuid)

    db.session.commit()

    sleep(3)
