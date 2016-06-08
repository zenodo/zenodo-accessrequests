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

from zenodo_accessrequests.helpers import Ordering, QueryOrdering


def test_selected(app):
    """Test selected."""
    assert 'a' == Ordering(['a', 'b'], 'a').selected()
    assert '-b' == Ordering(['a', 'b'], '-b').selected()
    assert Ordering(['a', 'b'], 'c').selected() is None
    assert Ordering(['a', 'b'], None).selected() is None


def test_reverse(app):
    """Test reverse."""
    assert '-a' == Ordering(['a', 'b'], 'a').reverse('a')
    assert 'a' == Ordering(['a', 'b'], '-a').reverse('a')
    assert 'b' == Ordering(['a', 'b'], 'a').reverse('b')
    assert 'b' == Ordering(['a', 'b'], '-a').reverse('b')
    assert Ordering(['a', 'b'], '-a').reverse('c') is None


def test_dir(app):
    """Test direction."""
    assert 'asc' == Ordering(['a', 'b'], 'a').dir('a')
    assert 'desc' == Ordering(['a', 'b'], '-a').dir('a')
    assert Ordering(['a', 'b'], 'a').dir('b') is None
    assert Ordering(['a', 'b'], '-a').dir('b') is None


def test_is_selected(app):
    """Test selected."""
    assert Ordering(['a', 'b'], 'a').is_selected('a') is True
    assert Ordering(['a', 'b'], '-a').is_selected('a') is True
    assert Ordering(['a', 'b'], 'a').is_selected('b') is False
    assert Ordering(['a', 'b'], '-a').is_selected('b') is False


class MockQuery(object):
    """Mock Query."""

    def order_by(self, val):
        """Mock order_by."""
        return val


def test_items(app):
    """Test selected."""
    q = MockQuery()
    assert 'a' == QueryOrdering(q, ['a', 'b'], 'a').items()
    # FIXME
    # assert 'a' == QueryOrdering(q, ['a', 'b'], '-a').items().element.text
    assert q == QueryOrdering(q, ['a', 'b'], 'c').items()
