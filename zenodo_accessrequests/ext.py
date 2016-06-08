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

"""Zenodo module for providing access request feature."""

from __future__ import absolute_import, print_function

from flask import request, session

from . import config


def verify_token():
    """Verify token and save in session if it's valid."""
    try:
        from .models import SecretLink
        token = request.args['token']
        # if the token is valid
        if token and SecretLink.validate_token(token, {}):
            # then save in session the token
            session['accessrequests-secret-token'] = token
    except KeyError:
        pass


class _AppState(object):

    def __init__(self, app):
        """Initialize state."""
        from .receivers import connect_receivers
        self.app = app
        connect_receivers()


class ZenodoAccessRequests(object):
    """Zenodo-AccessRequests extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.before_request(verify_token)
        self.init_config(app)
        state = _AppState(app=app)
        app.extensions['zenodo-accessrequests'] = state

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "ACCESSREQUESTS_BASE_TEMPLATE",
            app.config.get("BASE_TEMPLATE",
                           "zenodo_accessrequests/base.html"))
        app.config.setdefault(
            "ACCESSREQUESTS_SETTINGS_TEMPLATE",
            app.config.get("SETTINGS_TEMPLATE",
                           "zenodo_accessrequests/settings/base.html"))

        for k in dir(config):
            if k.startswith('ACCESSREQUESTS_'):
                app.config.setdefault(k, getattr(config, k))
