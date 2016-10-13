from __future__ import absolute_import
from __future__ import print_function
import os
from ...common._base import BaseServer
########################################################################
class Machines(BaseServer):
    """
       This resource represents a collection of all the server machines that
       have been registered with the site. It other words, it represents
       the total computing power of your site. A site will continue to run
       as long as there is one server machine online.
       For a server machine to start hosting GIS services, it must be
       grouped (or clustered). When you create a new site, a cluster called
       'default' is created for you.
       The list of server machines in your site can be dynamic. You can
       register additional server machines when you need to increase the
       computing power of your site or unregister them if you no longer
       need them.
    """
    _machines = None
    _json_dict = None
    _con = None
    _url = None
    _json = None
    _DatastoreMachines = None
    _Protocal = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - loads the machine information
        """
        super(Machines, self).__init__(url=url,
                                       connection=connection,
                                       initialize=initialize)
        self._url = url
        self._con = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def DatastoreMachines(self):
        """returns the datastore machine list"""
        if self._DatastoreMachines is None:
            self.init()
        return self._DatastoreMachines
    #----------------------------------------------------------------------
    @property
    def Protocol(self):
        """returns the protocal"""
        if self._Protocal is None:
            self.init()
        return self._Protocal
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """  returns the list of machines in the cluster """
        machines = []
        if self._machines is None:
            self.init()
        if isinstance(self._machines, list):
            for m in self._machines:
                machines.append(
                    Machine(url=self._url +"/%s" % m['machineName'],
                            connection=self._con))
        return machines
    #----------------------------------------------------------------------
    def get_machine(self, machineName):
        """returns a machine object for a given machine
           Input:
              machineName - name of the box ex: SERVER.DOMAIN.COM
        """
        url = self._url + "/%s" % machineName
        return Machine(url=url,
                       connection=self._con)
    #----------------------------------------------------------------------
    def register(self, machineName, adminURL):
        """
           For a server machine to participate in a site, it needs to be
           registered with the site. The server machine must have ArcGIS
           Server software installed and authorized.
           Registering machines this way is a "pull" approach to growing
           the site and is a convenient way when a large number of machines
           need to be added to a site. In contrast, a server machine can
           choose to join a site.
           Inputs:
              machineName - name of the server machine
              adminURL - URL wher ethe Administrator API is running on the
                         server machine.
                         Example: http://<machineName>:6080/arcgis/admin
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "machineName" : machineName,
            "adminURL" : adminURL
        }
        url = "%s/register" % self._url
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def rename(self, machineName, newMachineName):
        """
           You must use this operation if one of the registered machines
           has undergone a name change. This operation updates any
           references to the former machine configuration.
           By default, when the server is restarted, it is capable of
           identifying a name change and repairing itself and all its
           references. This operation is a manual call to handle the
           machine name change.
           Input:
              machineName - The former name of the server machine that is
                            registered with the site.
              newMachineName - The new name of the server machine.
           Output:
              JSON messages as dictionary
        """
        params = {
            "f" : "json",
            "machineName" : machineName,
            "newMachineName" : newMachineName
        }
        url = self._url + "/rename"
        return self._con.post(path=url, postdata=params)
########################################################################
class Machine(BaseServer):
    """
       A server machine represents a machine on which ArcGIS Server
       software has been installed and licensed. A site is made up one or
       more of such machines that work together to host GIS services and
       data and provide administrative capabilities for the site. Each
       server machine is capable of performing all these tasks and hence a
       site can be thought of as a distributed peer-to-peer network of such
       machines.
       A server machine communicates with its peers over a range of TCP and
       UDP ports that can be configured using the edit operation. For a
       server machine to host GIS services, it needs to be added to a
       cluster. Starting and stopping the server machine enables and
       disables, respectively, its ability to host GIS services.
       The administrative capabilities of the server machine are available
       through the ArcGIS Server Administrator API that can be accessed
       over HTTP(S). For a server machine to participate in a site, it must
       be registered with the site. A machine can participate in only one
       site at a time. To remove a machine permanently from the site, you
       can use the unregister operation.
    """
    _appServerMaxHeapSize = None
    _webServerSSLEnabled = None
    _webServerMaxHeapSize = None
    _platform = None
    _adminURL = None
    _machineName = None
    _ServerStartTime = None
    _webServerCertificateAlias = None
    _socMaxHeapSize = None
    _synchronize = None
    _configuredState = None
    _ports = None
    _json = None
    _json_dict = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - boolean - loads properties at creation of object
        """
        super(Machine, self).__init__(url=url,
                                      connection=connection,
                                      initialize=initialize)
        self._url = url
        self._con = connection
        self._currentURL = url
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def sslcertificates(self):
        """
        his resource lists all the certificates (self-signed and CA-signed)
        created for the server machine. The server securely stores these
        certificates inside a key store within the configuration store.
        Before you enable SSL on your server, you need to generate
        certificates and get them signed by a trusted certificate authority
        (CA). For your convenience, the server is capable of generating
        self-signed certificates that can be used during development or
        staging. However, it is critical that you get CA-signed
        certificates when standing up a production server.
        In order to get a certificate signed by a CA, you need to generate
        a CSR (certificate signing request) and then submit it to your CA.
        The CA will sign your certificate request which can then be
        imported into the server by using the import CA signed certificate
        operation.
        """
        params = {"f" : "json"}
        url = self._url + "/sslcertificates"
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def sslcertificate(self, alias):
        """
        A certificate represents a key pair that has been digitally signed
        and acknowledged by a Certifying Authority (CA). It is the most
        fundamental component in enabling SSL on your server.
        The Generate Certificate operation creates a new self-signed
        certificate and adds it to the keystore. In order for browsers and
        other HTTP client applications to trust the SSL connection on the
        server, this certificate must be digitally signed by a CA and then
        imported into the keystore. Even though a self-signed certificate
        can be used to enable SSL, it is recommended that you use a
        self-signed certificates only on staging or development servers.

        Parameters:
           alias - certificate name
        """
        url = self._url + "/sslcertificates/{cert}".format(cert=alias)
        params = {"f" : "json"}
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def delete_certificate(self, alias):
        """
        This operation deletes an SSL certificate from the key store. Once
        a certificate is deleted, it cannot be retrieved or used to enable
        SSL.

        Parameters:
           alias - certificate name
        """
        params = {"f" : "json"}
        url =  self._url + "/sslcertificates/{cert}/delete".format(cert=alias)
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def edit(self, adminURL, ports=None):
        """
        ArcGIS Server uses four ports for communication between GIS
        servers. When you create or join a site, these are assigned to
        ports 4000-4003. If any of those ports are in use by other
        applications, those ports are skipped and a corresponding number of
        additional ports are used beyond 4003.
        You must ensure that your firewall allows communication with other
        GIS server machines through four ports beginning with 4000 and not
        counting any port currently in use by another application. You can
        use this operation to see where the ports were assigned (and thus
        which ports you should open on your firewall) or use it to modify
        ArcGIS Server to use a different set of port numbers if there is a
        conflict.
        You'll notice that the ports are named according to their function.
        The port names do not have to match the port numbers between GIS
        server machines. For example, the NamingPort could be 4003 on one
        GIS server and 4006 on a different GIS server.

        Parameters:
           adminURL - url where the Administrator API is running on the
             server machine
           ports - dictionary - key/value of the name of the port with the
             number
        """
        url = self._url + "/edit"
        params = {"f":"json"}
        if ports is None:
            ports = {}
        for k,v in ports.items():
            params[k] = v
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def export_certificate(self, certName, out_folder):
        """
        This operation downloads an SSL certificate. The file returned by
        the server is an X.509 certificate. The downloaded certificate can
        then be imported into a client that is making HTTP requests.

        Parameters:
           certName - name of the certificate
        """
        params = {"f" : "json"}
        url = self._url + "/sslcertificates/{cert}/export".format(cert=certName)
        return self._con.download_to_folder(path=url,
                                            dir_name=out_folder)
    #----------------------------------------------------------------------
    def importRootCertificate(self, alias, rootCACertificate):
        """This operation imports a certificate authority (CA)'s root and intermediate certificates into the keystore."""
        url = self._url + "/sslcertificates/importRootOrIntermediate"
        files = [['rootCSCertificate', rootCACertificate, os.path.basename(rootCACertificate)]]
        params = {
            "f" : "json",
            "alias" : alias
        }
        return self._con.post(path=url,
                            postdata=params,
                            files=files)
    #----------------------------------------------------------------------
    def importExistingServerCertificate(self, alias, certPassword, certFile):
        """This operation imports an existing server certificate, stored in the PKCS #12 format, into the keystore."""
        url = self._url + "/sslcertificates/importExistingServerCertificate"
        files = [['certFile', certFile, os.path.basename(certFile)]]
        params = {
            "f" : "json",
            "alias" : alias,
            "certPassword" : certPassword
        }
        return self._con.post(path=url,
                            param_dict=params,
                            files=files)
    #----------------------------------------------------------------------
    def importCASignedCertificate(self, alias, caSignedCertificate):
        """This operation imports a certificate authority (CA)-signed SSL certificate into the key store."""
        url = self._url + "/sslcertificates/importCASignedCertificate"
        files = [['caSignedCertificate', caSignedCertificate, os.path.basename(caSignedCertificate)]]
        params = {
            "f" : "json",
            "alias" : alias
        }
        return self._con.post(path=url,
                          param_dict=params,
                          files=files)
    #----------------------------------------------------------------------
    def generate_certificate(self,
                             alias,
                             commonName,
                             orginization,
                             keyalg="RSA",
                             keysize=1024,
                             sigalg="SHA1withRSA",
                             organizationUnit="GIS",
                             city="Redlands",
                             state="California",
                             country="US",
                             validity=90,
                             SAN=None
                             ):
        """
        Use this operation to create a self-signed certificate or as a
        starting point for getting a production-ready CA-signed
        certificate. The server will generate a certificate for you and
        store it in its keystore.

        Parameters:
        alias - A unique name that easily identifies the certificate. This
         is required.
        keyalg - The algorithm used to generate the key pairs. The default
         is RSA.
        keysize - Specifies the size in bits to use when generating the
         cryptographic keys used to create the certificate. The larger the
         key size, the harder it is to break the encryption; however, the
         time to decrypt encrypted data increases with key size. For DSA,
         the key size can be between 512 and 1,024. For RSA, the
         recommended key size is 2,048 or greater.
        sigalg - Use the default (SHA1withRSA). If your organization has
         specific security restrictions, then one of the following
         algorithms can be used for DSA: SHA256withRSA, SHA384withRSA,
         SHA512withRSA, SHA1withDSA.
        commonName - Use the domain name of your server name as the common
         name.If your server will be accessed on the Internet through the
         URL https://www.gisserver.com:6443/arcgis/, use www.gisserver.com
         as the common name.
         If your server will only be accessible on your local area network
         (LAN) through the URL https://gisserver.domain.com:6443/arcgis,
         use gisserver as the common name.
        organizationalUnit - The name of your organizational unit, for
         example, GIS Department.
        organization - The name of your organization, for example, Esri.
         This is required.
        city - The name of the city or locality, for example, Redlands.
        state - The full name of your state or province, for example,
         California.
        country - The abbreviated code for your country, for example, US.
        validity - The total time in days during which this certificate
         will be valid, for example, 365. The default is 90.
        SAN - Subject Alternative Name - The subject alternative name (SAN)
         is an optional parameter that defines alternatives to the common
         name (CN) specified in the SSL certificate. There cannot be any
         spaces in the SAN parameter value.
         If no SAN is defined, a website can only be accessed (without SSL
         certificate errors) by using the common name in the URL. If a SAN
         is defined and a DNS name is present, the website can only be
         accessed by what is listed in the SAN. Multiple DNS names can be
         specified if desired. For example, the URLs https://www.esri.com,
         https://esri, and https://10.60.1.16 can be used to access the
         same site if the SSL certificate is created using the following
         SAN parameter value: DNS:www.esri.com,DNS:esri,IP:10.60.1.16
        """
        params = {"f" : "json",
                  "alias" : alias,
                  "keyalg" : keyalg,
                  "keysize" : keysize,
                  "sigalg" : sigalg,
                  "commonName" : commonName,
                  "organizationalUnit" : organizationUnit,
                  "organization" : orginization,
                  "city" : city,
                  "state" : state,
                  "country" : country,
                  "validity" : validity
                  }
        if SAN:
            params['SAN'] = SAN
        url = self._url + "/sslcertificates/generate"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def generate_CSR(self, certName):
        """
        This operation generates a certificate signing request (CSR) for a
        self-signed certificate. A CSR is required by a CA to create a
        digitally signed version of your certificate.

        Parameter:
          certName - name of the certificate to generate the CSR for.
        """
        url = "{base}/sslcertificates/{cert}/generateCSR".format(base=self._url,
                                                                 cert=certName)
        params = {"f" : "json"}
        return self._con.post(path=url, postdata=params)

    #----------------------------------------------------------------------
    @property
    def appServerMaxHeapSize(self):
        """ returns the app server max heap size """
        if self._appServerMaxHeapSize is None:
            self.init()
        return self._appServerMaxHeapSize
    #----------------------------------------------------------------------
    @property
    def webServerSSLEnabled(self):
        """ SSL enabled """
        if self._webServerSSLEnabled is None:
            self.init()
        return self._webServerSSLEnabled
    #----------------------------------------------------------------------
    @property
    def webServerMaxHeapSize(self):
        """ returns the web server max heap size """
        if self._webServerMaxHeapSize is None:
            self.init()
        return self._webServerMaxHeapSize
    #----------------------------------------------------------------------
    @property
    def platform(self):
        """ returns the platform information """
        if self._platform is None:
            self.init()
        return self._platform
    #----------------------------------------------------------------------
    @property
    def adminURL(self):
        """ returns the administration URL """
        if self._adminURL is None:
            self.init()
        return self._adminURL
    #----------------------------------------------------------------------
    @property
    def machineName(self):
        """ returns the machine name """
        if self._machineName is None:
            self.init()
        return self._machineName
    #----------------------------------------------------------------------
    @property
    def ServerStartTime(self):
        """ returns the server start date/time """
        if self._ServerStartTime is None:
            self.init()
        return self._ServerStartTime
    #----------------------------------------------------------------------
    @property
    def webServerCertificateAlias(self):
        """ returns the webserver cert alias"""
        if self._webServerCertificateAlias is None:
            self.init()
        return self._webServerCertificateAlias
    #----------------------------------------------------------------------
    @property
    def socMaxHeapSize(self):
        """ returns the soc's max heap size """
        if self._socMaxHeapSize is None:
            self.init()
        return self._socMaxHeapSize
    #----------------------------------------------------------------------
    @property
    def synchronize(self):
        """synchronize value"""
        if self._synchronize is None:
            self.init()
        return self._synchronize
    #----------------------------------------------------------------------
    @property
    def ports(self):
        """ returns the used ports """
        if self._ports is None:
            self.init()
        return self._ports
    #----------------------------------------------------------------------
    @property
    def configuredState(self):
        """ returns the configured state """
        if self._configuredState is None:
            self.init()
        return self._configuredState
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the state """
        uURL = self._url + "/status"
        params = {
            "f" : "json",
        }
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    def start(self):
        """ Starts the server machine """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/start"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def stop(self):
        """ Stops the server machine """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/stop"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def unregister(self):
        """
           This operation causes the server machine to be deleted from the
           Site.
           The server machine will no longer participate in the site or run
           any of the GIS services. All resources that were acquired by the
           server machine (memory, files, and so forth) will be released.
           Typically, you should only invoke this operation if the machine
           is going to be shut down for extended periods of time or if it
           is being upgraded.
           Once a machine has been unregistered, you can create a new site
           or join an existing site.
        """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/start"
        return self._con.post(path=uURL, postdata=params)
