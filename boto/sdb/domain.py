# Copyright (c) 2006,2007 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Represents an SDB Domain
"""
from boto.sdb.queryresultset import SelectResultSet

class Domain:
    
    def __init__(self, connection=None, name=None):
        self.connection = connection
        self.name = name
        self._metadata = None

    def __repr__(self):
        return 'Domain:%s' % self.name

    def __iter__(self):
        return iter(self.select("SELECT * FROM `%s`" % self.name))

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'DomainName':
            self.name = value
        else:
            setattr(self, name, value)

    def get_metadata(self):
        if not self._metadata:
            self._metadata = self.connection.domain_metadata(self)
        return self._metadata
    
    def put_attributes(self, item_name, attributes,
                       replace=True, expected_value=None):
        """
        Store attributes for a given item.

        :type item_name: string
        :param item_name: The name of the item whose attributes are being stored.

        :type attribute_names: dict or dict-like object
        :param attribute_names: The name/value pairs to store as attributes

        :type expected_value: list
        :param expected_value: If supplied, this is a list or tuple consisting
                               of a single attribute name and expected value.
                               The list can be of the form:
                                * ['name', 'value']
                               In which case the call will first verify
                               that the attribute "name" of this item has
                               a value of "value".  If it does, the delete
                               will proceed, otherwise a ConditionalCheckFailed
                               error will be returned.
                               The list can also be of the form:
                                * ['name', True|False]
                               which will simply check for the existence (True)
                               or non-existencve (False) of the attribute.

        :type replace: bool
        :param replace: Whether the attribute values passed in will replace
                        existing values or will be added as addition values.
                        Defaults to True.

        :rtype: bool
        :return: True if successful
        """
        return self.connection.put_attributes(self, item_name, attributes,
                                              replace, expected_value)

    def batch_put_attributes(self, items, replace=True):
        """
        Store attributes for multiple items.

        :type items: dict or dict-like object
        :param items: A dictionary-like object.  The keys of the dictionary are
                      the item names and the values are themselves dictionaries
                      of attribute names/values, exactly the same as the
                      attribute_names parameter of the scalar put_attributes
                      call.

        :type replace: bool
        :param replace: Whether the attribute values passed in will replace
                        existing values or will be added as addition values.
                        Defaults to True.

        :rtype: bool
        :return: True if successful
        """
        return self.connection.batch_put_attributes(self, items, replace)

    def get_attributes(self, item_name, attribute_name=None,
                       consistent_read=False, item=None):
        """
        Retrieve attributes for a given item.

        :type item_name: string
        :param item_name: The name of the item whose attributes are being retrieved.

        :type attribute_names: string or list of strings
        :param attribute_names: An attribute name or list of attribute names.  This
                                parameter is optional.  If not supplied, all attributes
                                will be retrieved for the item.

        :rtype: :class:`boto.sdb.item.Item`
        :return: An Item mapping type containing the requested attribute name/values
        """
        return self.connection.get_attributes(self, item_name, attribute_name,
                                              consistent_read, item)

    def delete_attributes(self, item_name, attributes=None,
                          expected_values=None):
        """
        Delete attributes from a given item.

        :type item_name: string
        :param item_name: The name of the item whose attributes are being deleted.

        :type attributes: dict, list or :class:`boto.sdb.item.Item`
        :param attributes: Either a list containing attribute names which will cause
                           all values associated with that attribute name to be deleted or
                           a dict or Item containing the attribute names and keys and list
                           of values to delete as the value.  If no value is supplied,
                           all attribute name/values for the item will be deleted.
                           
        :type expected_value: list
        :param expected_value: If supplied, this is a list or tuple consisting
                               of a single attribute name and expected value.
                               The list can be of the form:
                                * ['name', 'value']
                               In which case the call will first verify
                               that the attribute "name" of this item has
                               a value of "value".  If it does, the delete
                               will proceed, otherwise a ConditionalCheckFailed
                               error will be returned.
                               The list can also be of the form:
                                * ['name', True|False]
                               which will simply check for the existence (True)
                               or non-existencve (False) of the attribute.

        :rtype: bool
        :return: True if successful
        """
        return self.connection.delete_attributes(self, item_name, attributes,
                                                 expected_values)

    def select(self, query='', next_token=None, consistent_read=False, max_items=None):
        """
        Returns a set of Attributes for item names within domain_name that match the query.
        The query must be expressed in using the SELECT style syntax rather than the
        original SimpleDB query language.

        :type query: string
        :param query: The SimpleDB query to be performed.

        :rtype: iter
        :return: An iterator containing the results.  This is actually a generator
                 function that will iterate across all search results, not just the
                 first page.
        """
        return SelectResultSet(self, query, max_items = max_items, next_token=next_token,
                               consistent_read=consistent_read)
    
    def get_item(self, item_name):
        item = self.get_attributes(item_name)
        if item:
            item.domain = self
            return item
        else:
            return None

    def new_item(self, item_name):
        return self.connection.item_cls(self, item_name)

    def delete_item(self, item):
        self.delete_attributes(item.name)

    def to_xml(self, f=None):
        """Get this domain as an XML DOM Document
        :param f: Optional File to dump directly to
        :type f: File or Stream

        :return: File object where the XML has been dumped to
        :rtype: file
        """
        if not f:
            from tempfile import TemporaryFile
            f = TemporaryFile()
        print >>f,  '<?xml version="1.0" encoding="UTF-8"?>'
        print >>f,  '<Domain id="%s">' % self.name
        for item in self:
            print >>f, '\t<Item id="%s">' % item.name
            for k in item:
                print >>f, '\t\t<attribute id="%s">' % k
                values = item[k]
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    print >>f, '\t\t\t<value><![CDATA[',
                    if isinstance(value, unicode):
                        value = value.encode('utf-8', 'replace')
                    else:
                        value = unicode(value, errors='replace').encode('utf-8', 'replace')
                    f.write(value)
                    print >>f, ']]></value>'
                print >>f, '\t\t</attribute>'
            print >>f, '\t</Item>'
        print >>f, '</Domain>'
        f.flush()
        f.seek(0)
        return f


    def from_xml(self, doc):
        """Load this domain based on an XML document"""
        import xml.sax
        handler = DomainDumpParser(self)
        xml.sax.parse(doc, handler)
        return handler

    def delete(self):
        """
        Delete this domain, and all items under it
        """
        return self.connection.delete(self)


class DomainMetaData:
    
    def __init__(self, domain=None):
        self.domain = domain
        self.item_count = None
        self.item_names_size = None
        self.attr_name_count = None
        self.attr_names_size = None
        self.attr_value_count = None
        self.attr_values_size = None

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'ItemCount':
            self.item_count = int(value)
        elif name == 'ItemNamesSizeBytes':
            self.item_names_size = int(value)
        elif name == 'AttributeNameCount':
            self.attr_name_count = int(value)
        elif name == 'AttributeNamesSizeBytes':
            self.attr_names_size = int(value)
        elif name == 'AttributeValueCount':
            self.attr_value_count = int(value)
        elif name == 'AttributeValuesSizeBytes':
            self.attr_values_size = int(value)
        elif name == 'Timestamp':
            self.timestamp = value
        else:
            setattr(self, name, value)

import sys
from xml.sax.handler import ContentHandler
class DomainDumpParser(ContentHandler):
    """
    SAX parser for a domain that has been dumped
    """
    
    def __init__(self, domain):
        self.uploader = UploaderThread(domain)
        self.item_id = None
        self.attrs = {}
        self.attribute = None
        self.value = ""
        self.domain = domain

    def startElement(self, name, attrs):
        if name == "Item":
            self.item_id = attrs['id']
            self.attrs = {}
        elif name == "attribute":
            self.attribute = attrs['id']
        elif name == "value":
            self.value = ""

    def characters(self, ch):
        self.value += ch

    def endElement(self, name):
        if name == "value":
            if self.value and self.attribute:
                value = self.value.strip()
                attr_name = self.attribute.strip()
                if self.attrs.has_key(attr_name):
                    self.attrs[attr_name].append(value)
                else:
                    self.attrs[attr_name] = [value]
        elif name == "Item":
            self.uploader.items[self.item_id] = self.attrs
            # Every 20 items we spawn off the uploader
            if len(self.uploader.items) >= 20:
                self.uploader.start()
                self.uploader = UploaderThread(self.domain)
        elif name == "Domain":
            # If we're done, spawn off our last Uploader Thread
            self.uploader.start()

from threading import Thread
class UploaderThread(Thread):
    """Uploader Thread"""
    
    def __init__(self, domain):
        self.db = domain
        self.items = {}
        Thread.__init__(self)

    def run(self):
        try:
            self.db.batch_put_attributes(self.items)
        except:
            print "Exception using batch put, trying regular put instead"
            for item_name in self.items:
                self.db.put_attributes(item_name, self.items[item_name])
        print ".",
        sys.stdout.flush()
