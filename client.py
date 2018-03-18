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

import click

from context import socketcontext

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', default='127.0.0.1', prompt=True, type=click.STRING)
@click.option('--port', default=50008, prompt=True, type=click.INT)
@click.option('-c', '--command', default='helloworld', prompt=True, type=click.STRING)
@click.option('-f', '--file', type=click.File('rb'))
def main(host, port, command, file):
    with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
        except ConnectionRefusedError:
            click.secho('Error: connection refused.', fg='red')
            exit()
        click.secho('Connection established.', fg='green')
        sock.send(command.encode())
        if file:
            sock.send(b'!~file')
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                try:
                    sock.send(chunk)
                except ConnectionResetError:
                    click.secho('Error: connection reset on sending.', fg='red')
                    break
        data = b''
        while True:
            try:
                chunk = sock.recv(1024)
            except ConnectionResetError:
                click.secho('Error: connection reset on receiving.', fg='red')
                break
            if not chunk:
                break
            data += chunk
        click.echo('  Returned:\n    ' + click.style(data.decode().replace('\n', '\n    '), fg='cyan'))


if __name__ == '__main__':
    main()
