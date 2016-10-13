"""
_server.py contains functions and class to access ArcGIS Server.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
try:
    from arcgis import _impl
    #rom .arcgis import _impl
    #import arcgis
except:
    raise ImportError("The arcgis package is required for this add-in")
from .service._layerfactory import Layer
from .server.ags.catalog import Catalog
from .server.manage import AGSAdministration


class Server(object):
    """

    """
    _url = None
    _admin_url = None
    _token_url = None
    _username = None
    _password = None
    _key_file = None
    _cert_file = None
    _verify_cert = None
    _proxy_url = None
    _proxy_port = None
    _portal_con = None
    _logged_in = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None, token_url=None,
                 username=None, password=None,
                 key_file=None, cert_file=None,
                 verify_cert=True,
                 proxy_host=None, proxy_port=None,
                 portal_connection=None):
        """initializer"""
        self._logged_in = False
        self._admin_url, self._url = self._validate_url(url)
        self._token_url = token_url
        self._username = username
        self._password = password
        self._key_file = key_file
        self._cert_file = cert_file
        if verify_cert is None:
            verify_cert = True
        self._verify_cert = verify_cert
        self._proxy_url = proxy_host
        self._proxy_port = proxy_port
        self._portal_con = portal_connection
        self._con = self.__enter__()
    def _validate_url(self,url):
        """ensures the url given can be parsed and constructed into catalog url and
        administration url"""
        from six.moves.urllib_parse import urlparse
        p = urlparse(url)
        if len(p.path) > 1:
            path = p.path[1:].split('/')[0]
        else:
            path = "arcgis"
        return "%s://%s/%s/admin" % (p.scheme, p.netloc, path),"%s://%s/%s/rest" % (p.scheme, p.netloc, path)
    #----------------------------------------------------------------------
    def __enter__(self):
        """creates the connection class"""
        self._logged_in = True
        return _impl.connection._ArcGISConnection(baseurl=self._url,
                                 tokenurl=self._token_url,
                                 username=self._username,
                                 password=self._password,
                                 key_file=self._key_file,
                                 cert_file=self._cert_file,
                                 expiration=60,
                                 all_ssl=False,
                                 referer=None,
                                 proxy_host=self._proxy_url,
                                 proxy_port=self._proxy_port,
                                 connection=self._portal_con)#,
                                 #verify_cert=self._verify_cert)
    #----------------------------------------------------------------------
    def logout(self):
        """closes the connection to server"""
        self._logged_in = False
        self._con = None
    #----------------------------------------------------------------------
    def login(self):
        """logs into the server"""
        if self._logged_in == False:
            self.__enter__()
    #----------------------------------------------------------------------
    @property
    def logged_in(self):
        """boolean value that determines if a connection to server has been made"""
        return self._logged_in
    #----------------------------------------------------------------------
    @property
    def catalog(self):
        """returns a user's view of the server"""
        if self.logged_in:
            return Catalog(url=self._url,
                           connection=self._con,
                           initialize=True)
        return
    #----------------------------------------------------------------------
    @property
    def server_manager(self):
        """returns class to manage the ArcGIS Server"""
        if self._logged_in and \
           self._con._auth != 'ANON':
            from six.moves.urllib_parse import urlparse
            p = urlparse(self._url)
            url = "%s://%s/%s/admin" % (p.scheme, p.netloc, p.path[1:].split('/')[0])
            return AGSAdministration(url=url, connection=self._con)
        return
    #----------------------------------------------------------------------
    @staticmethod
    def get_service(self, service_url, connection=None):
        """
        returns a service object based on a connection
        """
        try:
            return Layer(url=service_url, connection=self._con)
        except:
            raise ValueError("Cannot access the service, verify the inputs")