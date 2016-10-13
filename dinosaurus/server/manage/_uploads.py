from __future__ import absolute_import
from __future__ import print_function
from ...common._base import BaseServer
import os
########################################################################
class Uploads(BaseServer):
    """
    This resource is a collection of all the items that have been uploaded
    to the server.
    See: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Uploads/02r3000001qr000000/
    """
    _uploads = None
    _con = None
    _json = None
    _json_dict = None
    _url = None

    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor"""
        super(Uploads, self).__init__(url=url,
                                      connection=connection)
        if url.lower().find("uploads") < -1:
            self._url = url + "/uploads"
        else:
            self._url = url
        self._con = connection
        self._json_dict = {}
        self._json = ""

    #----------------------------------------------------------------------
    @property
    def uploads(self):
        """
        returns a collection of all the items that have been uploaded to
        the server.
        """
        params = {
            "f" :"json"
        }
        return self._con.get(path=self._url,
                            params=params)
    #----------------------------------------------------------------------
    def delete_item(self, itemId):
        """
           Deletes the uploaded item and its configuration.
           Inputs:
              itemId - unique ID of the item
        """
        url = self._url + "/%s/delete" % itemId
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def item(self, itemId):
        """
        This resource represents an item that has been uploaded to the
        server. Various workflows upload items and then process them on the
        server. For example, when publishing a GIS service from ArcGIS for
        Desktop or ArcGIS Server Manager, the application first uploads the
        service definition (.SD) to the server and then invokes the
        publishing geoprocessing tool to publish the service.
        Each uploaded item is identified by a unique name (itemID). The
        pathOnServer property locates the specific item in the ArcGIS
        Server system directory.
        The committed parameter is set to true once the upload of
        individual parts is complete.
        """
        url = self._url + "/%s" % itemId
        params = {
            "f" : "json"
        }
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def upload_item(self, filePath, description):
        """"""
        url = self._url + "/upload"
        params = {
            "f" : "json"
        }
        files = [['itemFile',filePath, os.path.basename(filePath)]]
        return self._con.post(path=url,
                              postdata=params,
                              files=files)