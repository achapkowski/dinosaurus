"""
   Adminstration.py allows users to control ArcGIS Server 10.1+
   through the Administration REST API

"""
from __future__ import absolute_import
import json
from ...common._base import BaseServer
from . import _machines, _clusters
from . import _data, _info
from . import _kml, _logs
from . import _security, _services
from . import _system
from . import _uploads, _usagereports

########################################################################
class AGSAdministration(BaseServer):
    """
    Wrapper for the ArcGIS Server REST API

    Inputs:
       url - Administration REST URL
       securityHandler - security handler object for ArcGIS Server
       proxy_url - optional URL of a proxy
       proxy_port - optional port of a proxy
       initialize - default is false.  False means the object does not make
                    any REST calls until the object is actually needed,
                    whereas True means the object's properties are
                    initialized at creation.
    """
    _url = None
    _con = None
    _json_dict = None
    _json = None
    _acceptLanguage = None
    _currentVersion = None
    _resources = None
    _fullVersion = None
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """ populates server admin information """
        if self._url.lower().endswith('/admin') == False:
            self._url = "%s/admin" % self._url
        params = {
            "f": "json"
            }
        if connection:
            json_dict = connection.get(path=self._url,
                                       params=params)
        else:
            json_dict = self._con.get(path=self._url,
                                      params=params)
        self._json = json.dumps(json_dict)
        self._json_dict = json_dict
        missing = {}
        attributes = [attr for attr in dir(self)
                    if not attr.startswith('__') and \
                    not attr.startswith('_')]
        for k,v in json_dict.items():
            if k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                setattr(self, k, v)
                missing[k] = v
            del k, v
        self.__dict__.update(missing)
    #----------------------------------------------------------------------
    @property
    def acceptLanguage(self):
        """returns the accepted lanaguage"""
        if self._acceptLanguage is None:
            self.init()
        return self._acceptLanguage
    #----------------------------------------------------------------------
    @property
    def currentVersion(self):
        """returns the current version"""
        if self._currentVersion is None:
            self.init()
        return self._currentVersion
    #----------------------------------------------------------------------
    @property
    def resources(self):
        """returns the resources on the server"""
        if self._resources is None:
            self.init()
        return self._resources
    #----------------------------------------------------------------------
    @property
    def fullVersion(self):
        """returns the full version of the arcgis server software"""
        if self._fullVersion is None:
            self.init()
        return self._fullVersion
    #----------------------------------------------------------------------
    def create_site(self,
                   username,
                   password,
                   configStoreConnection,
                   directories,
                   cluster=None,
                   logsSettings=None,
                   runAsync=False
                   ):
        """
        This is the first operation that you must invoke when you install
        ArcGIS Server for the first time. Creating a new site involves:

          -Allocating a store to save the site configuration
          -Configuring the server machine and registering it with the site
          -Creating a new cluster configuration that includes the server
           machine
          -Configuring server directories
          -Deploying the services that are marked to auto-deploy

        Because of the sheer number of tasks, it usually takes a little
        while for this operation to complete. Once a site has been created,
        you can publish GIS services and deploy them to your server
        machines.

        Inputs:
           username - The name of the administrative account to be used by
             the site. This can be changed at a later stage.
           password - The credentials of the administrative account.
           configStoreConnection - A JSON object representing the
             connection to the configuration store. By default, the
             configuration store will be maintained in the ArcGIS Server
             installation directory.
           directories - A JSON object representing a collection of server
             directories to create. By default, the server directories will
             be created locally.
           cluster - An optional cluster configuration. By default, the
             site will create a cluster called 'default' with the first
             available port numbers starting from 4004.
           logsSettings - Optional log settings.
           runAsync - A flag to indicate if the operation needs to be run
             asynchronously. Values: true | false
        """
        url = self._url + "/createNewSite"
        params = {
            "f" : "json",
            "cluster" : cluster,
            "directories" : directories,
            "username" : username,
            "password" : password,
            "configStoreConnection" : configStoreConnection,
            "logSettings" : logsSettings,
            "runAsync" : runAsync
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def join_site(self, adminURL, username, password):
        """
        The Join Site operation is used to connect a server machine to an
        existing site. This is considered a 'push' mechanism, in which a
        server machine pushes its configuration to the site. For the
        operation to be successful, you need to provide an account with
        administrative privileges to the site.
        When an attempt is made to join a site, the site validates the
        administrative credentials, then returns connection information
        about its configuration store back to the server machine. The
        server machine then uses the connection information to work with
        the configuration store.
        If this is the first server machine in your site, use the Create
        Site operation instead.

        Inputs:
           adminURL - The site URL of the currently live site. This is
            typically the Administrator Directory URL of one of the server
            machines of a site.
           username - The name of an administrative account for the site.
           password - The password of the administrative account.
        """
        url = self._url + "/joinSite"
        params = {
            "f" : "json",
            "adminURL" : adminURL,
            "username" : username,
            "password" : password
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def delete_site(self):
        """
        Deletes the site configuration and releases all server resources.
        This is an unrecoverable operation. This operation is well suited
        for development or test servers that need to be cleaned up
        regularly. It can also be performed prior to uninstall. Use caution
        with this option because it deletes all services, settings, and
        other configurations.
        This operation performs the following tasks:
          - Stops all server machines participating in the site. This in
            turn stops all GIS services hosted on the server machines.
          - All services and cluster configurations are deleted.
          - All server machines are unregistered from the site.
          - All server machines are unregistered from the site.
          - The configuration store is deleted.
        """
        url = self._url + "/deleteSite"
        params = {
            "f" : "json"
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def export_site(self, location=None):
        """
        Exports the site configuration to a location you specify as input
        to this operation.

        Inputs:
           location - A path to a folder accessible to the server where the
            exported site configuration will be written. If a location is
            not specified, the server writes the exported site
            configuration file to directory owned by the server and returns
            a virtual path (an HTTP URL) to that location from where it can
            be downloaded.

        """
        url = self._url + "/exportSite"
        params = {
            "f" : "json"
        }
        if location is not None:
            params['location'] = location
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def import_site(self, location):
        """
        This operation imports a site configuration into the currently
        running site. Importing a site means replacing all site
        configurations (including GIS services, security configurations,
        and so on) of the currently running site with those contained in
        the site configuration file you supply as input. The input site
        configuration file can be obtained through the exportSite
        operation.
        This operation will restore all information included in the backup,
        as noted in exportSite. When it is complete, this operation returns
        a report as the response. You should review this report and fix any
        problems it lists to ensure your site is fully functioning again.
        The importSite operation lets you restore your site from a backup
        that you created using the exportSite operation.

        Input:
           location - A file path to an exported configuration or an ID
            referencing the stored configuration on the server.
        """
        url = self._url + "/importSite"
        params = {
            "f" : "json",
            "location" : location
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    @property
    def publicKey(self):
        """gets the public key"""
        url = self._url + "/publicKey"
        params = {
            "f" : "json",
        }
        return self._con.get(path=url,
                            params=params)
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """gets a reference to the machines object"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "machines" in self.resources:
            url = self._url + "/machines"
            return _machines.Machines(url,
                                      connection=self._con,
                                      initialize=False)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def data(self):
        """returns the reference to the data functions as a class"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "data" in self.resources:
            url = self._url + "/data"
            return _data.Data(url=url,
                              connection=self._con,
                              initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def info(self):
        """
        A read-only resource that returns meta information about the server
        """
        if self._resources is None:
            self.init()
        url = self._url + "/info"
        return _info.Info(url=url,
                          connection=self._con,
                          initialize=True)
    #----------------------------------------------------------------------
    @property
    def clusters(self):
        """returns the clusters functions if supported in resources"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "clusters" in self.resources:
            url = self._url + "/clusters"
            return _clusters.Cluster(url=url,
                                     connection=self._con,
                                     initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def services(self):
        """
        Gets the services object which will provide the ArcGIS Server's
        admin information about services and folders.
        """
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "services" in self.resources:
            url = self._url + "/services"
            return _services.Services(url=url,
                                      connection=self._con,
                                      initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def usagereports(self):
        """
        Gets the services object which will provide the ArcGIS Server's
        admin information about the usagereports.
        """
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "usagereports" in self.resources:
            url = self._url + "/usagereports"
            return _usagereports.UsageReports(url=url,
                                              connection=self._con,
                                              initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def kml(self):
        """returns the kml functions for server"""
        url = self._url + "/kml"
        return _kml.KML(url=url,
                        connection=self._con,
                        initialize=True)
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """returns an object to work with the site logs"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "logs" in self.resources:
            url = self._url + "/logs"
            return _logs.Log(url=url,
                             connection=self._con,
                             initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def security(self):
        """returns an object to work with the site security"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "security" in self.resources:
            url = self._url + "/security"
            return _security.Security(url=url,
                                      connection=self._con,
                                      initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def system(self):
        """returns an object to work with the site system"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "system" in self.resources:
            url = self._url + "/system"
            return _system.System(url=url,
                                  connection=self._con,
                                  initialize=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def uploads(self):
        """returns an object to work with the site uploads"""
        if self._resources is None:
            self.init()
        if isinstance(self.resources, list) and \
           "uploads" in self.resources:
            url = self._url + "/uploads"
            return _uploads.Uploads(url=url,
                                    connection=self._con,
                                    initialize=True)
        else:
            return None
