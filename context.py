#!/usr/bin/python
# -*- coding: utf-8 -*-

# rrcontrol - remote control software
# Copyright (C) 2018  Ranx

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import socket
from contextlib import contextmanager


@contextmanager
def socketcontext(*args, **kw):
    """
    :rtype: socket
    """
    s = socket.socket(*args, **kw)
    try:
        yield s
    finally:
        s.close()
        # print('Socket closed')


@contextmanager
def acceptconnectioncontext(s):
    conn, addr = s.accept()
    try:
        yield (conn, addr)
    finally:
        conn.close()
        # print('Connection closed')
