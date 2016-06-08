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


"""Admin interface to shared links."""

from __future__ import absolute_import, print_function

from flask_admin.contrib.sqla import ModelView
from flask_babelex import gettext as _

from .models import AccessRequest, SecretLink


class AccessRequestAdmin(ModelView):
    """Access requests admin view."""

    can_create = False
    can_edit = True
    can_delete = True

    column_list = (
        'status', 'recid', 'sender_email', 'receiver', 'created', 'modified',
        'link'
    )


class SecretLinkAdmin(ModelView):
    """Secret links admin view."""

    _can_create = False
    _can_edit = True
    _can_delete = True

    acc_view_action = 'cfgaccessrequests'
    acc_edit_action = 'cfgaccessrequests'
    acc_delete_action = 'cfgaccessrequests'

    column_list = (
        'recid', 'owner', 'created', 'expires_at', 'revoked_at', 'title'
    )


accessrequest_adminview = dict(
    modelview=AccessRequestAdmin,
    model=AccessRequest,
    category=_('Shared links')
)
secretlinks_adminview = dict(
    modelview=SecretLinkAdmin,
    model=SecretLink,
    category=_('Shared links')
)
