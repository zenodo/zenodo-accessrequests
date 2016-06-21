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

"""Views for creating access requests and sending access restricted files."""

from __future__ import absolute_import, print_function

from datetime import datetime
from flask import Blueprint, abort, current_app, flash, redirect, \
    render_template, request, url_for
from flask_login import current_user

from flask_babelex import gettext as _

from werkzeug.local import LocalProxy
from invenio_db import db

from ..forms import AccessRequestForm
from ..models import AccessRequest, RequestStatus
from ..tokens import EmailConfirmationSerializer

blueprint = Blueprint(
    'zenodo_accessrequests',
    __name__,
    url_prefix="/record",
    static_folder="../static",
    template_folder="../templates",
)


#
# Template filters
#


@blueprint.app_template_filter(name="is_restricted")
def is_restricted(record):
    """Template filter to check if a record is restricted."""
    return record.get('access_right') == 'restricted' and \
        record.get('access_conditions') and \
        record.get('owners', [])


@blueprint.app_template_filter()
def is_embargoed(record):
    """Template filter to check if a record is embargoed."""
    return record.get('access_right') == 'embargoed' and \
        record.get('embargo_date') and \
        record.get('embargo_date') > datetime.utcnow().date()


@blueprint.app_template_filter()
def is_removed(record):
    """Template filter to check if a record is removed."""
    return {'primary': 'SPAM'} in record.get('collections', [])

#
# Views
#


def access_request(pid, record, template):
    """Create an access request."""
    recid = int(pid.pid_value)
    datastore = LocalProxy(
        lambda: current_app.extensions['security'].datastore)

    # Record must be in restricted access mode.
    if record.get('access_right') != 'restricted' or \
       not record.get('access_conditions'):
        abort(404)

    # Record must have an owner and owner must still exists.
    owners = record.get('owners', [])
    record_owners = [datastore.find_user(id=owner_id) for owner_id in owners]
    if not record_owners:
        abort(404)

    sender = None
    initialdata = dict()

    # Prepare initial form data
    if current_user.is_authenticated:
        sender = current_user
        initialdata['email'] = current_user.email
        if current_user.profile:
            initialdata['full_name'] = current_user.profile.full_name

    # Normal form validation
    form = AccessRequestForm(formdata=request.form, **initialdata)

    if form.validate_on_submit():
        accreq = AccessRequest.create(
            recid=recid,
            receiver=record_owners[0],
            sender_full_name=form.data['full_name'],
            sender_email=form.data['email'],
            justification=form.data['justification'],
            sender=sender
        )
        db.session.commit()

        if accreq.status == RequestStatus.EMAIL_VALIDATION:
            flash(_(
                "Email confirmation needed: We have sent you an email to "
                "verify your address. Please check the email and follow the "
                "instructions to complete the access request."),
                category='info')
        else:
            flash(_("Access request submitted."), category='info')
        return redirect(url_for('invenio_records_ui.recid', pid_value=recid))

    return render_template(
        template,
        pid=pid,
        record=record,
        form=form,
        owners=record_owners,
    )


def confirm(pid, record, template):
    """Confirm email address."""
    recid = int(pid.pid_value)

    token = request.view_args['token']

    # Validate token
    data = EmailConfirmationSerializer().validate_token(token)
    if data is None:
        flash(_("Invalid confirmation link."), category='danger')
        return redirect(url_for("invenio_records_ui.recid", pid_value=recid))

    # Validate request exists.
    r = AccessRequest.query.get(data['id'])
    if not r:
        abort(404)

    # Confirm email address.
    if r.status != RequestStatus.EMAIL_VALIDATION:
        abort(404)

    r.confirm_email()
    db.session.commit()
    flash(_("Email validated and access request submitted."), category='info')

    return redirect(url_for("invenio_records_ui.recid", pid_value=recid))
