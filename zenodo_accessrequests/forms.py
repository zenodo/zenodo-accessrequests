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


"""Forms for module."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

from flask_babelex import gettext as _
from flask_security.forms import email_required, email_validator
from flask_wtf import FlaskForm
from wtforms import DateField, HiddenField, StringField, SubmitField, \
    TextAreaField, validators

from .widgets import Button


def validate_expires_at(form, field):
    """Validate that date is in the future."""
    if form.accept.data:
        if not field.data or datetime.utcnow().date() >= field.data:
            raise validators.StopValidation(_(
                "Please provide a future date."
            ))
        if not field.data or \
                datetime.utcnow().date() + timedelta(days=365) < field.data:
            raise validators.StopValidation(_(
                "Please provide a date no more than 1 year into the future."
            ))


class AccessRequestForm(FlaskForm):
    """Form for requesting access to a record."""

    full_name = StringField(
        label=_("Full name"),
        description=_("Required."),
        validators=[validators.DataRequired()]
    )

    email = StringField(
        label=_("Email address"),
        description=_(
            "Required. Please carefully check your email address. If the owner"
            " grants access, a secret link will be sent to this email address."
        ),
        validators=[email_required, email_validator]
    )

    justification = TextAreaField(
        label=_("Justification"),
        description=_(
            "Required. Please thoroughly justify how you fulfil the "
            "conditions listed above."),
        validators=[validators.DataRequired()],
    )


class ApprovalForm(FlaskForm):
    """Form used to approve/reject requests."""

    request = HiddenField()

    message = TextAreaField(
        label=_("Message to requester"),
        description=_(
            "Required if you reject the request. Optional if you accept the"
            " request."),
    )
    expires_at = DateField(
        label=_('Expires'),
        description=_(
            'Format: YYYY-MM-DD. Required if you accept the request. The '
            'access will automatically be revoked on this date. Date must be '
            'within the next year.'
        ),
        default=lambda: datetime.utcnow().date() + timedelta(days=31),
        validators=[validate_expires_at, validators.Optional()],
    )

    accept = SubmitField(_("Accept"), widget=Button(icon="fa fa-check"))
    reject = SubmitField(_("Reject"), widget=Button(icon="fa fa-times"))

    def validate_accept(form, field):
        """Validate that accept have not been set."""
        if field.data and form.reject.data:
            raise validators.ValidationError(
                _("Both reject and accept cannot be set at the same time.")
            )

    def validate_reject(form, field):
        """Validate that accept have not been set."""
        if field.data and form.accept.data:
            raise validators.ValidationError(
                _("Both reject and accept cannot be set at the same time.")
            )

    def validate_message(form, field):
        """Validate message."""
        if form.reject.data and not field.data.strip():
            raise validators.ValidationError(
                _("You are required to provide message to the requester when"
                  " you reject a request.")
            )


class DeleteForm(FlaskForm):
    """Form used for delete buttons."""

    link = HiddenField()

    delete = SubmitField(_("Revoke"), widget=Button(icon="fa fa-trash-o"))
