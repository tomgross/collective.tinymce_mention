# -*- coding: utf-8 -*-
from collective.tinymce_mention.interfaces import ICollectiveTinymceMentionLayer  # noqa
from collective.tinymce_mention.interfaces import ISimpleSerializer
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.utils import iterSchemata
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.outputfilters.interfaces import IFilter
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.relationfield.interfaces import IRelationValue
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import implementer_only
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope.schema import getFields

import re


class DollarVarReplacer(dict):

    """
    Initialize with a dictionary, then self.sub returns a string
    with all ${key} substrings replaced with values looked
    up from the dictionary.
    >>> from collective.easyform import api
    >>> adict = {'one':'two', '_two':'three', '.two':'four'}
    >>> dvr = api.DollarVarReplacer(adict)
    >>> dvr.sub('one one')
    'one one'
    >>> dvr.sub('one ${one}')
    'one two'
    >>> dvr.sub('one ${two}')
    'one ???'
    Skip any key beginning with _ or .
    >>> dvr.sub('one ${_two}')
    'one ???'
    >>> dvr.sub('one ${.two}')
    'one ???'
    """

    dollar_pattern = re.compile(r'\$\{(.+?)\}')
    not_found = ''

    def sub(self, s):
        return self.dollar_pattern.sub(self.repl, s)

    def repl(self, mo):
        key = mo.group(1)
        if key and key[0] not in ['_', '.']:
            return self.get(key, self.not_found)
        else:
            return self.not_found


@implementer_only(ISimpleSerializer)
@adapter(Interface)
class TextSerializer(object):

    def __init__(self, field):
        self.field = field

    def __call__(self, context):
        value = self.field.get(context)
        if not value:
            return ''
        return value


@adapter(schema_interfaces.IDatetime)
class DateTimeSerializer(TextSerializer):

    def __call__(self, context):
        value = self.field.get(context)
        request = getRequest()
        plone_view = api.content.get_view(
            name='plone', context=context, request=request)
        return plone_view.toLocalizedTime(value(), long_format=True)


@adapter(schema_interfaces.IList)
class ListSerializer(TextSerializer):
    """ Serializer for lists """

    def __call__(self, context):
        value = super(ListSerializer, self).__call__(context)
        return u', '.join([ISimpleSerializer(x) for x in value])


@adapter(schema_interfaces.ITuple)
class TupleSerializer(ListSerializer):
    """ Serializer for tuples """


@adapter(IRelationValue)
class RelationValueSerializer(TextSerializer):
    """ Serializer for related values """

    def __call__(self, context):
        value = self.field.get(context)
        if not value:
            return ''
        return uuidToURL(value)


@implementer(IFilter)
class PlaceHolderReplacer(object):
    order = 1000

    def __init__(self, context, request):
        # context is site
        self.context = request.PUBLISHED.context
        self.request = request

    def is_enabled(self):
        return ICollectiveTinymceMentionLayer.providedBy(self.request)

    def check_permission(self, permission_name, obj):
        if permission_name is None:
            return True
        return True

    def __call__(self, data):
        values = {}

        for schema in iterSchemata(self.context):

            read_permissions = mergedTaggedValueDict(
                schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():

                # We don't support richtext fields because we
                # don't want endless recursions and it is hard
                # to detect where we come from
                if IRichText.providedBy(field):
                    continue

                if not self.check_permission(
                        read_permissions.get(name), self.context):
                    continue

                values[name] = ISimpleSerializer(field)(self.context)

        dr = DollarVarReplacer(values)
        return dr.sub(data)
