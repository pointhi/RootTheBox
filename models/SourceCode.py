# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import os

from uuid import uuid4
from hashlib import sha1
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String, Unicode, Integer
from models import dbsession
from models.BaseModels import DatabaseObject
from libs.ValidationError import ValidationError
from libs.ConfigManager import ConfigManager


class SourceCode(DatabaseObject):

    '''
    Holds the source code for a box which can be purchased from the
    source code market.
    '''

    DIR = 'source_code_market/'

    uuid = Column(String(36),
                  unique=True,
                  nullable=False,
                  default=lambda: str(uuid4())
                  )

    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    _price = Column(Integer, nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    checksum = Column(String(40))
    _file_name = Column(String(64), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Returns a the object with a given _uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_box_id(cls, _id):
        return dbsession.query(cls).filter_by(box_id=_id).first()

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        fname = value.replace('\n', '').replace('\r', '')
        self._file_name = unicode(os.path.basename(fname))[:64]

    @property
    def data(self):
        config = ConfigManager.instance()
        with open(config.file_uploads_dir + self.DIR + self.uuid, 'rb') as fp:
            return fp.read().decode('base64')

    @data.setter
    def data(self, value):
        config = ConfigManager.instance()
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.byte_size = len(value)
        self.checksum = sha1(value).hexdigest()
        with open(config.file_uploads_dir + self.DIR + self.uuid, 'wb') as fp:
            fp.write(value.encode('base64'))

    def delete_data(self):
        ''' Remove the file from the file system, if it exists '''
        config = ConfigManager.instance()
        fpath = config.file_uploads_dir + self.DIR + self.uuid
        if os.path.exists(fpath) and os.path.isfile(fpath):
            os.unlink(fpath)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        try:
            self._price = abs(int(value))
        except ValueError:
            raise ValidationError("Price must be an integer")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = unicode(value)[:1024]

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'price': self.price,
            'description': self.description,
        }
