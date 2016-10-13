from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import datetime
import time
import json
import copy
import os
import tempfile
import uuid
from ._spatial import json_to_featureclass
from ._geom import BaseGeometry
from ._geom import Geometry, Point, MultiPoint, Polygon, Polyline, SpatialReference
#TODD: from arcgis.geom import BaseGeometry, Geometry, Point, MultiPoint, Polygon, Polyline, SpatialReference
__all__ = ["Feature", "FeatureSet"]
#----------------------------------------------------------------------
def _date_handler(obj):
    if isinstance(obj, datetime.datetime):
        return local_time_to_online(obj)
    else:
        return obj
#----------------------------------------------------------------------
def local_time_to_online(dt=None):
    """
       converts datetime object to a UTC timestamp for AGOL
       Inputs:
          dt - datetime object
       Output:
          Long value
    """
    if dt is None:
        dt = datetime.datetime.now()

    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset =  (time.altzone if is_dst else time.timezone)

    return (time.mktime(dt.timetuple())  * 1000) + (utc_offset *1000)
########################################################################
class Feature(object):
    """ returns a feature  """
    _geom = None
    _json = None
    _dict = None
    _geom = None
    _geomType = None
    _attributes = None
    _wkid = None
    #----------------------------------------------------------------------
    def __init__(self, geometry=None, attributes=None):
        """Constructor"""
        self._dict = {

            }
        if geometry is not None:
            self._dict["geometry"] = geometry
        if attributes is not None:
            self._dict["attributes"] = attributes
    #----------------------------------------------------------------------
    def set_value(self, field_name, value):
        """ sets an attribute value for a given field name """
        if field_name in self.fields:
            if not value is None:
                self._dict['attributes'][field_name] = value
                self._json = json.dumps(self._dict, default=_date_handler)
            else:
                pass
        elif field_name.upper() in ['SHAPE', 'SHAPE@', "GEOMETRY"]:
            if isinstance(value, BaseGeometry):
                if isinstance(value, Point):
                    self._dict['geometry'] = {
                    "x" : value['x'],
                    "y" : value['y']
                    }
                elif isinstance(value, MultiPoint):
                    self._dict['geometry'] = {
                        "points" : value['points']
                    }
                elif isinstance(value, Polyline):
                    self._dict['geometry'] = {
                        "paths" : value['paths']
                    }
                elif isinstance(value, Polygon):
                    self._dict['geometry'] = {
                        "rings" : value['rings']
                    }
                else:
                    return False
                self._json = json.dumps(self._dict, default=_date_handler)
        else:
            return False
        return True
    #----------------------------------------------------------------------
    def get_value(self, field_name):
        """ returns a value for a given field name """
        if field_name in self.fields:
            return self._dict['attributes'][field_name]
        elif field_name.upper() in ['SHAPE', 'SHAPE@', "GEOMETRY"]:
            return self._dict['geometry']
        return None
    #----------------------------------------------------------------------
    @property
    def as_dict(self):
        """returns the feature as a dictionary"""
        return self._dict
    #----------------------------------------------------------------------
    @property
    def as_row(self):
        """ converts a feature to a list for insertion into an insert cursor
            Output:
               [row items], [field names]
               returns a list of fields and the row object
        """
        fields = self.fields
        row = [""] * len(fields)
        for k,v in self._attributes.items():
            row[fields.index(k)] = v
            del v
            del k
        if self.geometry is not None:
            row.append(self.geometry)
            fields.append("SHAPE@")
        return row, fields
    #----------------------------------------------------------------------
    @property
    def geometry(self):
        """returns the feature geometry"""
        if self._geom is None:
            self._geom = self._dict['geometry']
        return self._geom
    @geometry.setter
    def geometry(self, value):
        """gets/sets a feature's geometry"""
        self._geom = value
        self._dict['geometry'] = value
    #----------------------------------------------------------------------
    @property
    def attributes(self):
        """returns the feature attributes"""
        if self._attributes is None:
            self._attributes = self._dict['attributes']
        return self._attributes
    @attributes.setter
    def attributes(self, value):
        """gets/sets a feature's attributes"""
        self._attributes = value
        self._dict['attributes'] = value
    #----------------------------------------------------------------------
    @property
    def fields(self):
        """ returns a list of feature fields """
        self._attributes = self._dict['attributes']
        return self._attributes.keys()
    #----------------------------------------------------------------------
    @property
    def geometry_type(self):
        """ returns the feature's geometry type """
        if self._geomType is None:
            if self.geometry is not None:
                self._geomType = self.geometry.type
            else:
                self._geomType = "Table"
        return self._geomType
    #----------------------------------------------------------------------
    @classmethod
    def from_json(cls, json_str):
        """returns a feature from a JSON string"""
        feature = json.loads(json_str)
        return cls(feature['geometry'], feature['attributes'])
    #----------------------------------------------------------------------
    @classmethod
    def from_dict(cls, feature):
        """returns a featureset from a dict"""
        return cls(feature['geometry'], feature['attributes'])
    #----------------------------------------------------------------------
    @staticmethod
    def fc_to_features(dataset):
        """
           converts a dataset to a list of feature objects, if ArcPy is available
           Input:
              dataset - path to table or feature class
           Output:
              list of feature objects
        """
        try:
            import arcpy
            arcpyFound = True
        except:
            arcpyFound = False
        if arcpyFound:
            desc = arcpy.Describe(dataset)
            fields = [field.name for field in arcpy.ListFields(dataset) if field.type not in ['Geometry']]
            date_fields = [field.name for field in arcpy.ListFields(dataset) if field.type =='Date']
            non_geom_fields = copy.deepcopy(fields)
            features = []
            if hasattr(desc, "shapeFieldName"):
                fields.append("SHAPE@JSON")
            del desc
            with arcpy.da.SearchCursor(dataset, fields) as rows:
                for row in rows:
                    row = list(row)
                    for df in date_fields:
                        if row[fields.index(df)] != None:
                            row[fields.index(df)] = int((_date_handler(row[fields.index(df)])))
                    template = {
                        "attributes" : dict(zip(non_geom_fields, row))
                    }
                    if "SHAPE@JSON" in fields:
                        template['geometry'] = \
                            json.loads(row[fields.index("SHAPE@JSON")])

                    features.append(
                        Feature.from_dict(template)
                    )
                    del row
            return features
        return None

    #----------------------------------------------------------------------
    def __str__(self):
        """"""
        return json.dumps(self.as_dict)

########################################################################
class FeatureSet(object):
    """
    A FeatureSet is a collection of Features.
    FeatureSets are commonly used as input/output with several Geoprocessing
    Tools, as well as the output of query() methods of feature layers.

    This FeatureSet contains Feature objects, including the values for the
    fields requested by the user. For layers, if you request geometry
    information, the geometry of each feature is also returned in the
    featureSet. For tables, the featureSet does not include geometries.
    If a spatialReference is not specified at the featureSet level, the
    featureSet will assume the spatialReference of its first feature. If
    the spatialReference of the first feature is also not specified, the
    spatial reference will be UnknownCoordinateSystem.
    """
    _fields = None
    _features = None
    _hasZ = None
    _hasM = None
    _geometryType = None
    _spatialReference = None
    _objectIdFieldName = None
    _globalIdFieldName = None
    _displayFieldName = None
    _allowedGeomTypes = ["esriGeometryPoint","esriGeometryMultipoint","esriGeometryPolyline",
                         "esriGeometryPolygon","esriGeometryEnvelope"]
    #----------------------------------------------------------------------
    def __init__(self,
                 features,
                 fields=None,
                 hasZ=False,
                 hasM=False,
                 geometryType=None,
                 spatialReference=None,
                 displayFieldName=None,
                 objectIdFieldName=None,
                 globalIdFieldName=None):
        """Constructor"""
        self._fields = fields
        self._features = features
        self._hasZ = hasZ
        self._hasM = hasM
        self._geometryType = geometryType
        self._spatialReference = spatialReference
        self._displayFieldName = displayFieldName
        self._objectIdFieldName = objectIdFieldName
        self._globalIdFieldName = globalIdFieldName

        g0 = None
        f = features[0]
        if isinstance(f, Feature):
            g0 = f.geometry
        else:
            g0 = f['geometry']

        if spatialReference is None:
            if 'spatialReference' in g0:
                self._spatialReference = g0['spatialReference']

        geometry = Geometry(g0)
        if geometryType is None:
            if isinstance(geometry, Polyline):
                self._geometryType = "esriGeometryPolyline"
            elif isinstance(geometry, Polygon):
                self._geometryType = "esriGeometryPolygon"
            elif isinstance(geometry, Point):
                self._geometryType = "esriGeometryPoint"
            elif isinstance(geometry, MultiPoint):
                self._geometryType = "esriGeometryMultipoint"
            else:
                raise AttributeError("Invalid geometry type")

    #----------------------------------------------------------------------
    def __str__(self):
        """returns object as string"""
        return json.dumps(self.value)
    #----------------------------------------------------------------------
    @property
    def value(self):
        """returns object as dictionary"""
        val = {
            "features" : [f.as_dict for f in self._features]
            }

        if self._objectIdFieldName is not None:
            val["objectIdFieldName"] = self._objectIdFieldName
        if self._displayFieldName is not None:
            val["displayFieldName"] = self._displayFieldName
        if self._globalIdFieldName is not None:
            val["globalIdFieldName"] = self._globalIdFieldName
        if self._spatialReference is not None:
            val["sr"] = self._spatialReference
        if self._geometryType is not None:
            val["geometryType"] = self._geometryType
        if self._hasZ:
            val["hasZ"] = self._hasZ
        if self._hasM:
            val["hasM"] = self._hasM

        return val

        #return {
        #    "objectIdFieldName" : self._objectIdFieldName,
        #    "displayFieldName" : self._displayFieldName,
        #    "globalIdFieldName" : self._globalIdFieldName,
        #    "geometryType" : self._geometryType,
        #    "spatialReference" : self._spatialReference,
        #    "hasZ" : self._hasZ,
        #    "hasM" : self._hasM,
        #    "fields" : self._fields,
        #    "features" : [f.as_dict for f in self._features]
        #}
    #----------------------------------------------------------------------
    @property
    def to_json(self):
        """converts the object to JSON"""
        return json.dumps(self.value)
    #----------------------------------------------------------------------
    def __iter__(self):
        """featureset iterator on features in feature set"""
        for feature in self._features:
            yield feature
    #----------------------------------------------------------------------
    def __len__(self):
        """returns the number of features in feature set"""
        return len(self._features)
    #----------------------------------------------------------------------
    @staticmethod
    def from_json(json_str):
        """returns a featureset from a JSON string"""
        jd = json.loads(json_str)
        return from_dict(jd)
#----------------------------------------------------------------------
    @staticmethod
    def from_dict(fsdict):
        """returns a featureset from a dict"""
        jd = fsdict
        features = []
        if 'fields' in jd:
            fields = jd['fields']
        else:
            fields = {'fields':[]}
        if 'features' in jd:
            for feat in jd['features']:
                features.append(Feature.from_dict(feat))
        return FeatureSet(features=features, fields=fields,
                          hasZ=jd['hasZ'] if 'hasZ' in jd else False,
                          hasM=jd['hasM'] if 'hasM' in jd else False,
                          geometryType=jd['geometryType'] if 'geometryType' in jd else None,
                          objectIdFieldName=jd['objectIdFieldName'] if 'objectIdFieldName' in jd else None,
                          globalIdFieldName=jd['globalIdFieldName'] if 'globalIdFieldName' in jd else None,
                          displayFieldName=jd['displayFieldName'] if 'displayFieldName' in jd else None,
                          spatialReference=jd['spatialReference'] if 'spatialReference' in jd else None)
    #----------------------------------------------------------------------
    @property
    def fields(self):
        """gets the featureset's fields"""
        return self._fields
    #----------------------------------------------------------------------
    @property
    def spatialReference(self):
        """gets the featureset's spatial reference"""
        return self._spatialReference
    #----------------------------------------------------------------------
    @spatialReference.setter
    def spatialReference(self, value):
        """sets the featureset's spatial reference"""
        if isinstance(value, SpatialReference):
            self._spatialReference = value
        elif isinstance(value, int):
            self._spatialReference = SpatialReference(wkid=value)
        elif isinstance(value, str) and \
             str(value).isdigit():
            self._spatialReference = SpatialReference(wkid=int(value))
    #----------------------------------------------------------------------
    @property
    def hasZ(self):
        """gets/sets the Z-property"""
        return self._hasZ
    #----------------------------------------------------------------------
    @hasZ.setter
    def hasZ(self, value):
        """gets/sets the Z-property"""
        if isinstance(value, bool):
            self._hasZ = value
    #----------------------------------------------------------------------
    @property
    def hasM(self):
        """gets/set the M-property"""
        return self._hasM
    #----------------------------------------------------------------------
    @hasM.setter
    def hasM(self, value):
        """gets/set the M-property"""
        if isinstance(value, bool):
            self._hasM = value
    #----------------------------------------------------------------------
    @property
    def geometryType(self):
        """gets/sets the geometry Type"""
        return self._geometryType
    #----------------------------------------------------------------------
    @geometryType.setter
    def geometryType(self, value):
        """gets/sets the geometry Type"""
        if value in self._allowedGeomTypes:
            self._geometryType = value
    #----------------------------------------------------------------------
    @property
    def objectIdFieldName(self):
        """gets/sets the object id field"""
        return self._objectIdFieldName
    #----------------------------------------------------------------------
    @objectIdFieldName.setter
    def objectIdFieldName(self, value):
        """gets/sets the object id field"""
        self._objectIdFieldName = value
    #----------------------------------------------------------------------
    @property
    def globalIdFieldName(self):
        """gets/sets the globalIdFieldName"""
        return self._globalIdFieldName
    #----------------------------------------------------------------------
    @globalIdFieldName.setter
    def globalIdFieldName(self, value):
        """gets/sets the globalIdFieldName"""
        self._globalIdFieldName = value
    #----------------------------------------------------------------------
    @property
    def displayFieldName(self):
        """gets/sets the displayFieldName"""
        return self._displayFieldName
    #----------------------------------------------------------------------
    @displayFieldName.setter
    def displayFieldName(self, value):
        """gets/sets the displayFieldName"""
        self._displayFieldName = value
    #----------------------------------------------------------------------
    def save(self, saveLocation, outName):
        """
        Saves a featureset object to a feature class
        Input:
           saveLocation - output location of the data
           outName - name of the table the data will be saved to
                Types:
                    *.csv - CSV file returned
                    *.json - text file with json
                    * If no extension, a shapefile if the path is a
                        folder, a featureclass if the path is a GDB

        """
        filename, file_extension = os.path.splitext(outName)
        if (file_extension == ".csv"):
            res = os.path.join(saveLocation,outName)
            import sys
            if sys.version_info[0] == 2:
                access = 'wb+'
                kwargs = {}
            else:
                access = 'wt+'
                kwargs = {'newline':''}
            with open(res, access, **kwargs) as csvFile:
                import csv
                f = csv.writer(csvFile)
                fields = []
                #write the headers to the csv
                for field in self.fields:
                    fields.append(field['name'])
                f.writerow(fields)

                newRow = []
                #Loop through the results and save each to a row
                for feature in self:
                    newRow = []
                    for field in self.fields:
                        newRow.append(feature.get_value(field['name']))
                    f.writerow(newRow)
                csvFile.close()
            del csvFile
        elif (file_extension == ".json"):
            res = os.path.join(saveLocation,outName)
            with open(res, 'wb') as writer:

                json.dump(self.value, writer, sort_keys = True, indent = 4, ensure_ascii=False)
                writer.flush()
                writer.close()
            del writer

        else:
            tempDir =  tempfile.gettempdir()
            tempFile = os.path.join(tempDir, "%s.json" % uuid.uuid4().hex)
            with open(tempFile, 'wt') as writer:
                writer.write(self.toJSON)
                writer.flush()
                writer.close()
            del writer
            res = json_to_featureclass(json_file=tempFile,
                                       out_fc=os.path.join(saveLocation, outName))
            os.remove(tempFile)
        return res
    #----------------------------------------------------------------------
    @property
    def features(self):
        """gets the features in the FeatureSet"""
        return self._features
    @property
    def fields(self):
        """gets the fieldsin the FeatureSet"""
        return self._fields
    @fields.setter
    def fields(self, fields):
        """sets the fieldsin the FeatureSet"""
        self._fields = fields
