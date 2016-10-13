"""
This provides access to a server and it's services for non administrative
functions.  This allows developers to access a REST service just like a
user/developer would.
"""
from __future__ import absolute_import
from six.moves.urllib_parse import urlparse
import json
from ...common._base import BaseServer
from ...service._layerfactory import Layer
__all__ = ['Catalog']
########################################################################
class Catalog(BaseServer):
    """This object represents an ArcGIS Server instance"""
    _url = None
    _con = None
    _json = None
    _json_dict = None
    _folders = None
    _services = None
    _currentVersion = None
    _location = None
    _currentFolder = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor"""
        #super(Catalog, self).__init__(url, connection,initialize)
        self._url = self._validateurl(url=url)
        self._con = connection
        self._location = self._url
        self._currentFolder = "root"

        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def _validateurl(self, url):
        """assembles the server url"""
        parsed = urlparse(url)
        parts = parsed.path[1:].split('/')
        if len(parts) == 0:
            self._adminUrl = "%s://%s/arcgis/admin" % (parsed.scheme, parsed.netloc)
            return "%s://%s/arcgis/rest/services" % (parsed.scheme, parsed.netloc)
        elif len(parts) > 0:
            self._adminUrl = "%s://%s/%s/admin" % (parsed.scheme, parsed.netloc, parts[0])
            return "%s://%s/%s/rest/services" % (parsed.scheme, parsed.netloc, parts[0])
    #----------------------------------------------------------------------
    def init(self, connection=None, folder='root'):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        if folder == "root":
            url = self.root
        else:
            url = self.location
        if connection is None:
            connection = self._con
        missing = {}
        json_dict = connection.get(path=url, params=params)
        self._json_dict = json_dict
        self._json = json.dumps(json_dict)
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        for k,v in json_dict.items():
            if k == "folders":
                pass
            elif k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                missing[k] = v
                setattr(self, k,v)
        json_dict = connection.get(path=self.root,
                                 params=params)
        for k,v in json_dict.items():
            if k == 'folders':
                v.insert(0, 'root')
                setattr(self, "_"+ k, v)
        self.__dict__.update(missing)
    #----------------------------------------------------------------------
    @property
    def root(self):
        """gets the url of the class"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def admin(self):
        """points to the adminstrative side of ArcGIS Server"""
        if self._con.security_method != "ANONYMOUS" or \
           self._con.is_logged_in() == False:
            from ..manage import AGSAdministration
            return AGSAdministration(url=self._adminUrl,
                                     connection=self._con,
                                     initialize=False)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def location(self):
        """returns the current url position in the server folder structure"""
        return self._location
    #----------------------------------------------------------------------
    @property
    def currentVersion(self):
        """gets the current version of arcgis server"""
        if self._currentVersion is None:
            self.init()
        return self._currentVersion
    #----------------------------------------------------------------------
    @property
    def user(self):
        """gets the logged in user"""
        params = {"f" : "json"}
        url = "%s/self" % self.root.replace("/services", "")
        return self._con.get(path=url,
                         params=params)
    #----------------------------------------------------------------------
    @property
    def info(self):
        """gets the site's information"""
        params = {"f" : "json"}
        url = "%s/info" % self.root.replace("/services", "")
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def services(self):
        """gets the services in the current folder"""
        if self._services is None:
            self.init()
        layers = []
        for service in self._services:
            layers.append(Layer(url="{base}/{name}/{servicetype}".format(
                base=self._location,
                name=service['name'],
                servicetype=service['type']
                ), connection=self._con))
        return layers
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """returns the folders on server"""
        if self._folders is None:
            self.init(folder="root")
        return self._folders
    #----------------------------------------------------------------------
    @property
    def currentFolder(self):
        """gets/sets the current folder name"""
        return self._currentFolder
    #----------------------------------------------------------------------
    @currentFolder.setter
    def currentFolder(self, value):
        """gets/sets the current folder name"""
        if value in self.folders:
            if value.lower() != 'root':
                self._currentFolder = value
                self._location = "%s/%s" % (self.root, value)
            else:
                self._currentFolder = value
                self._location = self.root
            self.init(folder=value)

