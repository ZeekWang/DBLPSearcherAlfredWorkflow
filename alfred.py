# -*- coding: utf-8 -*-

# Copyright 2013 Dr. Jan Müller

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

"""
You should run your script via /bin/bash with all escape options ticked.
The command line should be
python yourscript.py "{query}" arg2 arg3 ...
"""
UNESCAPE_CHARACTERS = u""" ;()"""

_MAX_RESULTS_DEFAULT = 9

preferences = plistlib.readPlist('info.plist')
bundleid = preferences['bundleid']

class Item(object):
    @classmethod
    def unicode(cls, value):
        try:
            items = iter(value.items())
        except AttributeError:
            return unicode(value)
        else:
            return dict(map(unicode, item) for item in items)

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml()).decode('utf-8')

    def xml(self):
        item = Element(u'item', self.unicode(self.attributes))
        for attribute in (u'title', u'subtitle', u'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            if len(value) == 2 and isinstance(value[1], dict):
                (value, attributes) = value
            else:
                attributes = {}
            SubElement(item, attribute, self.unicode(attributes)).text = self.unicode(value)
        return item

def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])

def config():
    return _create('config')

def decode(s):
    return unicodedata.normalize('NFD', s.decode('utf-8'))

def uid(uid):
    return u'-'.join(map(str, (bundleid, uid)))

def unescape(query, characters=None):
    for character in (UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace('\\%s' % character, character)
    return query

def work(volatile):
    path = {
        True: '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data',
        False: '~/Library/Application Support/Alfred 2/Workflow Data'
    }[bool(volatile)]
    return _create(os.path.join(os.path.expanduser(path), bundleid))

def write(text):
    sys.stdout.write(text)

def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')

def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path