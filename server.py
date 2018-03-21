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

# TODO: == COMPLETED == webcam screenshot
# TODO: file response
# TODO: == COMPLETED == require password to connect
# TODO: mouse move and freeze
# TODO: encryption

import shlex
import socket
import subprocess
from base64 import b64decode

import click
from cv2 import VideoCapture, imencode

from context import socketcontext, acceptconnectioncontext

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', default='127.0.0.1', prompt=True, type=click.STRING)
@click.option('--port', default=50008, prompt=True, type=click.INT)
@click.option('--password', '-p', default='123321', prompt=True, hide_input=True, type=click.STRING)
@click.option('--recv-data-limit', default=1024 * 100, type=click.INT,
              help='the maximum amount of data, that can be received (in bytes)')
def main(host, port, password, recv_data_limit):
    with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(1)
        click.echo('Started server on {}:{}.'.format(host, port))
        data_handler = DataHandler()
        while True:
            with acceptconnectioncontext(sock) as (conn, addr):
                conn.settimeout(1.5)
                click.secho('Connection from {}:{}.'.format(addr[0], addr[1]), fg='yellow')
                try:
                    if not conn.recv(16).rstrip() == password.encode():
                        click.secho('Error: authorization failed.', fg='red')
                        continue
                except ConnectionResetError:
                    click.secho('Error: connection reset.', fg='red')
                    continue
                click.secho('Authorization succeeded.', fg='green')
                data = b''
                for i in range(int(recv_data_limit / 1024)):
                    try:
                        chunk = conn.recv(1024)
                    except ConnectionResetError:
                        click.secho('Error: connection reset.', fg='red')
                        break
                    except socket.timeout:
                        break
                    if not chunk:
                        break
                    data += chunk
                response = data_handler.handle(data)
                if len(response) < 1024:
                    try:
                        click.echo('  Response:\n    ' + click.style(response.decode().replace('\n', '\n    '),
                                                                     fg='cyan'))
                    except UnicodeDecodeError:
                        click.secho('Error: UnicodeDecodeError while decoding the response.', fg='red')
                try:
                    conn.send(response)
                except ConnectionResetError:
                    click.secho('Error: connection reset.', fg='red')


class DataHandler:
    def __init__(self):
        self.data = ''
        self.file = None

    def handle(self, data: bytes):
        limiter = b64decode('IX5maWxl')
        if limiter in data:
            data, self.file = data[:data.index(limiter)], data[data.index(limiter) + len(limiter):]
        try:
            self.data = shlex.split(data.decode())
        except ValueError:
            return b'Invalid command, error while parsing.'
        click.echo('  Received command: ' + click.style(' '.join(self.data), fg='cyan'))
        handlers = {
            'helloworld': self.__hello_world_handler,
            'echo': self.__echo,
            'savefile': self.__save_file,
            'exec': self.__exec,
            'webcamphoto': self.__webcam_photo,
            'exit': self.__exit_handler
        }
        if self.data[0].lower() not in handlers:
            return b'Unknown command.'
        return handlers[self.data[0].lower()]()

    @staticmethod
    def __hello_world_handler():
        return b'Hello World'

    def __exec(self):
        result = subprocess.run(' '.join(self.data[1:]), stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                                shell=True)
        return result.stdout.decode('cp866').encode()

    def __echo(self):
        if len(self.data) > 1:
            click.echo(' '.join(self.data[1:]))
            return b'Successfully.'
        return b'Not enough arguments.'

    def __save_file(self):
        if len(self.data) > 1 and self.file:
            try:
                with open(self.data[1], 'wb') as f:
                    f.write(self.file)
            except Exception as e:
                error_msg = 'Error: {}: {}'.format(type(e).__name__, e)
                click.secho(error_msg, fg='red')
                return error_msg
            return b'Successfully.'
        return b'Input or destination file not specified.'

    @staticmethod
    def __webcam_photo():
        cam = VideoCapture(0)
        s, img = cam.read()
        if s:
            return imencode('.jpg', img)[1]
        return b'Error while reading from webcam.'

    @staticmethod
    def __exit_handler():
        exit()


if __name__ == '__main__':
    main()
