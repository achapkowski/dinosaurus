from __future__ import absolute_import
import json
from collections import OrderedDict
from arcgis._impl.connection import _ArcGISConnection
###########################################################################
class BasePortal(OrderedDict):
    _url = None
    _con = None
    _json_dict = None
    _json = None
    def __init__(self, connection, url, initialize=False):
        """constructor"""
        super(BasePortal, self).__init__()
        self._con = connection
        self._url = url
        self._json_dict = None
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """loads the properties"""
        params = {"f" : "json"}
        missing = {}
        if connection is None:
            connection = self._con
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        result = connection.get(path=self._url, params=params)
        self._json_dict = result
        self._json = json.dumps(result)
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        if isinstance(result, dict):
            self._json_dict = result
            for k,v in result.items():
                if k in attributes:
                    setattr(self, "_" + k, v)
                else:
                    missing[k] = v
                    setattr(self, k, v)
                del k,v
        else:
            raise RuntimeError("Could not connect to the service: %s" % result)
        if len(missing.keys()) > 0:
            self.__dict__.update(missing)
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the services properties"""
        self.init(connection=self._con)
    #----------------------------------------------------------------------
    def __str__(self):
        if self._json_dict is None:
            self.init()
        val = self._json_dict
        if val is None:
            return "{}"
        return json.dumps(self._json_dict)
    #----------------------------------------------------------------------
    def __repr__(self):
        """representation object"""
        return "{classtype}({data})".format(
            classtype=self.__class__.__name__,
            data=self.__str__())
    #----------------------------------------------------------------------
    def __iter__(self):
        """creates iterable for classes properties"""
        if self._json_dict is None:
            self.init()
        for k,v in self._json_dict.items():
            yield k,v
    #----------------------------------------------------------------------
    @property
    def connection(self):
        """gets/sets the connection object"""
        return self._con
    #----------------------------------------------------------------------
    @connection.setter
    def connection(self, value):
        """gets/sets the connection object"""
        if isinstance(value, _ArcGISConnection):
            self._con = value
            self.refresh()
        else:
            raise ValueError("connection must be of type _ArcGISConnection")
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    @url.setter
    def url(self, value):
        """gets/sets the service url"""
        self._url = value
        self.refresh()
###########################################################################
class BaseService(OrderedDict):
    _con = None
    _url = None
    _portal = None
    _gis = None
    _item = None
    _json_dict = None
    _json = None
    def __init__(self, item=None, gis=None, url=None,
                 connection=None, initialize=True,
                 **kwargs):
        """class initializer"""
        super(BaseService, self).__init__(**{'item' : item,
                                             'gis' : gis,
                                             'url' : url,
                                             'connection' : connection,
                                             'initialize' : False})
        if url is None and \
           item is None:
            raise ValueError("Either an Portal Item or URL must be provided to the service")
        if item is None and \
           gis is None and \
           connection is None:
            raise ValueError("A connection object is required to access the service")
        self._url = url
        self._gis = gis
        self._item = item

        if item is not None:
            if self._url is None:
                self._url = item.url
            if self._portal is None:
                self._portal = item._portal
            if self.connection is None:
                self.connection = item._portal.con
        if gis is not None:
            self._gis = gis
            if self.connection is None:
                self.connection = gis._portal.con
        self.connection = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """loads the properties into the class"""
        if connection is None:
            connection = self._con
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        params = {"f":"json"}
        result = connection.post(self._url, params)
        self._json_dict = result
        for k,v in result.items():
            if k in attributes:
                setattr(self, "_"+ k, v)
                self[k] = v
            else:
                self[k] = v
        if isinstance(result, dict):
            self.__dict__.update(result)
            super(BaseService, self).update(result)
    #----------------------------------------------------------------------
    @property
    def connection(self):
        """gets/sets the connection object"""
        return self._con
    #----------------------------------------------------------------------
    @connection.setter
    def connection(self, value):
        """gets/sets the connection object"""
        if isinstance(value, _ArcGISConnection):
            self._con = value
            self.refresh()
        elif value is None:
            self._con = value
        else:
            raise ValueError("connection must be of type _ArcGISConnection")
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    @url.setter
    def url(self, value):
        """gets/sets the service url"""
        self._url = value
        self.refresh()
    #----------------------------------------------------------------------
    def __str__(self):
        if self._json_dict is None:
            self.init()
        val = self._json_dict
        if val is None:
            return "{}"
        return json.dumps(self._json_dict)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "{classname}({data})".format(
            classname=self.__class__.__name__,
            data=self.__str__())
    #----------------------------------------------------------------------
    def __iter__(self):
        """creates iterable for classes properties"""
        for k,v in self._json_dict.items():
            yield k,v
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the properties of a given service"""
        self.init()

###########################################################################
class BaseServer(OrderedDict):
    _con = None
    _url = None
    _json_dict = None
    _json = None
    def __init__(self, url, connection=None, initialize=True, **kwargs):
        """class initializer"""
        super(BaseServer, self).__init__()
        self._url = url
        if isinstance(connection, _ArcGISConnection):
            self._con = connection
        else:
            raise ValueError("connection must be of type _ArcGISConnection")
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """loads the properties into the class"""
        if connection is None:
            connection = self._con
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        params = {"f":"json"}
        result = connection.get(path=self._url,
                                params=params)
        self._json_dict = result
        for k,v in result.items():
            if k in attributes:
                setattr(self, "_"+ k, v)
                self[k] = v
            else:
                self[k] = v
        self.__dict__.update(result)
    #----------------------------------------------------------------------
    @property
    def connection(self):
        """gets/sets the connection object"""
        return self._con
    #----------------------------------------------------------------------
    @connection.setter
    def connection(self, value):
        """gets/sets the connection object"""
        if isinstance(value, _ArcGISConnection):
            self._con = value
            self.refresh()
        else:
            raise ValueError("connection must be of type _ArcGISConnection")
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    @url.setter
    def url(self, value):
        """gets/sets the service url"""
        self._url = value
        self.refresh()
    #----------------------------------------------------------------------
    def __str__(self):
        if self._json_dict is None:
            self.init()
        val = self._json_dict
        if val is None:
            return "{}"
        return json.dumps(self._json_dict)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "{classname}({data})".format(
            classname=self.__class__.__name__,
            data=self.__str__())
    #----------------------------------------------------------------------
    def __iter__(self):
        """creates iterable for classes properties"""
        for k,v in self._json_dict.items():
            yield k,v
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the properties of a given service"""
        self.init()
