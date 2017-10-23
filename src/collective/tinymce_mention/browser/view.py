# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from Products.Five import BrowserView
from zope.component import getMultiAdapter

import json


class GetJsonSchemaView(BrowserView):

    ignore = [
        '@components', 'parent', 'text', 'relatedItems', 'version',
        'UID', 'layout',
        'content', 'customContentLayout'   # Mosaic fields
    ]

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        serializer = getMultiAdapter(
            (self.context, self.request), ISerializeToJson)
        json_context = [
            {'name': name, 'value': value}
            for name, value in serializer().items()
            if name not in self.ignore
        ]
        return json.dumps(json_context)
