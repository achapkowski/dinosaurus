"""

.. module:: _geometry.py
   :platform: Windows, Linux
   :synopsis: Represents functions/classes that represents a geometry
              service.
.. moduleauthor:: Esri

"""
from __future__ import absolute_import
import json
from ..common._geom import MultiPoint, Point
from ..common._geom import Polygon, Envelope
from ..common._geom import Polyline, Geometry
from ..common._base import BaseService
from arcgis.lyr import GISService

########################################################################
class GeometryService(BaseService):
    """
    A geometry service contains utility methods that provide access to
    sophisticated and frequently used geometric operations. An ArcGIS
    Server web site can only expose one geometry service with the static
    name GeometryService.
    """

    def __init__(self, url, gis=None):
        super(GeometryService, self).__init__(url, gis)

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Geometry Service':
            raise TypeError("item must be a type of Geometry Service, not " + item.type)
        return cls(item.url, item._gis)

    #----------------------------------------------------------------------
    def areas_and_lengths(self,
                        polygons,
                        lengthUnit,
                        areaUnit,
                        calculationType,
                        sr=4326):
        """
           The areasAndLengths operation is performed on a geometry service
           resource. This operation calculates areas and perimeter lengths
           for each polygon specified in the input array.

           Inputs:
              polygons - The array of polygons whose areas and lengths are
                         to be computed.
              lengthUnit - The length unit in which the perimeters of
                           polygons will be calculated. If calculationType
                           is planar, then lengthUnit can be any esriUnits
                           constant. If lengthUnit is not specified, the
                           units are derived from sr. If calculationType is
                           not planar, then lengthUnit must be a linear
                           esriUnits constant, such as esriSRUnit_Meter or
                           esriSRUnit_SurveyMile. If lengthUnit is not
                           specified, the units are meters. For a list of
                           valid units, see esriSRUnitType Constants and
                           esriSRUnit2Type Constant.
              areaUnit - The area unit in which areas of polygons will be
                         calculated. If calculationType is planar, then
                         areaUnit can be any esriUnits constant. If
                         areaUnit is not specified, the units are derived
                         from sr. If calculationType is not planar, then
                         areaUnit must be a linear esriUnits constant such
                         as esriSRUnit_Meter or esriSRUnit_SurveyMile. If
                         areaUnit is not specified, then the units are
                         meters. For a list of valid units, see
                         esriSRUnitType Constants and esriSRUnit2Type
                         constant.
                         The list of valid esriAreaUnits constants include,
                         esriSquareInches | esriSquareFeet |
                         esriSquareYards | esriAcres | esriSquareMiles |
                         esriSquareMillimeters | esriSquareCentimeters |
                         esriSquareDecimeters | esriSquareMeters | esriAres
                         | esriHectares | esriSquareKilometers.
              calculationType -  The type defined for the area and length
                                 calculation of the input geometries. The
                                 type can be one of the following values:
                                 planar - Planar measurements use 2D
                                          Euclidean distance to calculate
                                          area and length. Th- should
                                          only be used if the area or
                                          length needs to be calculated in
                                          the given spatial reference.
                                          Otherwise, use preserveShape.
                                 geodesic - Use this type if you want to
                                          calculate an area or length using
                                          only the vertices of the polygon
                                          and define the lines between the
                                          points as geodesic segments
                                          independent of the actual shape
                                          of the polygon. A geodesic
                                          segment is the shortest path
                                          between two points on an ellipsoid.
                                 preserveShape - This type calculates the
                                          area or length of the geometry on
                                          the surface of the Earth
                                          ellipsoid. The shape of the
                                          geometry in its coordinate system
                                          is preserved.
           Output:
              JSON as dictionary
        """
        url = self._url + "/areasAndLengths"
        params = {
            "f" : "json",
            "lengthUnit" : lengthUnit,
            "areaUnit" : {"areaUnit" : areaUnit},
            "calculationType" : calculationType,
            'sr' : sr
        }
        if isinstance(polygons, list) and len(polygons) > 0:
            p = polygons[0]
            if isinstance(p, Polygon):
                if hasattr(p, 'spatialReference'):
                    params['sr'] = p.spatialReference
                params['polygons'] = polygons
            elif isinstance(p, dict):
                params['polygons'] = polygons
            del p
        elif isinstance(polygons, dict):
            params['polygons'] = [polygons]
        elif isinstance(polygons, Polygon):
            params['polygons'] = [polygons]
        else:
            return "No polygons provided, please submit a list of polygon geometries"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def __geometryListToGeomTemplate(self, geometries):
        """
            converts a list of common.Geometry objects to the geometry
            template value
            Input:
               geometries - list of common.Geometry objects
            Output:
               Dictionary in geometry service template
        """
        template = {"geometryType": None,
                    "geometries" : []}
        if isinstance(geometries, list) and len(geometries) > 0:
            for g in geometries:
                if isinstance(g,dict):
                    g = Geometry(g)
                if isinstance(g, Polyline):
                    template['geometryType'] = "esriGeometryPolyline"
                elif isinstance(g, Polygon):
                    template['geometryType'] = "esriGeometryPolygon"
                elif isinstance(g, Point):
                    template['geometryType'] = "esriGeometryPoint"
                elif isinstance(g, MultiPoint):
                    template['geometryType'] = "esriGeometryMultipoint"
                elif isinstance(g, Envelope):
                    template['geometryType'] = "esriGeometryEnvelope"
                else:
                    raise AttributeError("Invalid geometry type")
                template['geometries'].append(g)
                del g
            return template
        return template
    #----------------------------------------------------------------------
    def __geometryToGeomTemplate(self, geometry):
        """
           Converts a single geometry object to a geometry service geometry
           template value.

           Input:
              geometry - geometry object
           Output:
              python dictionary of geometry template
        """
        template = {"geometryType": None,
                    "geometry" : None}
        if isinstance(geometry, dict):
            geometry = Geometry(geometry)
        if isinstance(geometry, Polyline):
            template['geometryType'] = "esriGeometryPolyline"
        elif isinstance(geometry, Polygon):
            template['geometryType'] = "esriGeometryPolygon"
        elif isinstance(geometry, Point):
            template['geometryType'] = "esriGeometryPoint"
        elif isinstance(geometry, MultiPoint):
            template['geometryType'] = "esriGeometryMultipoint"
        elif isinstance(geometry, Envelope):
            template['geometryType'] = "esriGeometryEnvelope"
        else:
            raise AttributeError("Invalid geometry type")
        template['geometry'] = geometry
        return template
    #----------------------------------------------------------------------
    def __geomToStringArray(self, geometries, returnType="str"):
        """ function to convert the geomtries to strings """
        listGeoms = []
        for g in geometries:
            if isinstance(g, dict):
                g = Geometry(g)
            if isinstance(g, Point):
                listGeoms.append(g)
            elif isinstance(g, Polygon):
                listGeoms.append(g)
            elif isinstance(g, Polyline):
                listGeoms.append({'paths' : g['paths']})
        if returnType == "str":
            return json.dumps(listGeoms)
        elif returnType == "list":
            return listGeoms
        else:
            return json.dumps(listGeoms)
    #----------------------------------------------------------------------
    def _process_results(self, results):
        if isinstance(results, list):
            vals = []
            for result in results:
                if isinstance(result, dict):
                    vals.append(Geometry(result))
                del result
            return vals
        elif isinstance(results, dict):
            if 'geometries' in results:
                return self._process_results(results['geometries'])
            elif 'geometry' in results:
                return Geometry(results['geometry'])
            else:
                return Geometry(results)
        else:
            return results
    #----------------------------------------------------------------------
    def auto_complete(self,
                     polygons=None,
                     polylines=None,
                     sr=None
                     ):
        """
           The autoComplete operation simplifies the process of
           constructing new polygons that are adjacent to other polygons.
           It constructs polygons that fill in the gaps between existing
           polygons and a set of polylines.

           Inputs:
              polygons - array of Polygon objects
              polylines - list of Polyline objects
              sr - spatial reference of the input geometries WKID
        """
        url = self._url + "/autoComplete"
        params = {"f":"json"}
        if polygons is None:
            polygons = []
        if polylines is None:
            polylines = []
        if sr is not None:
            params['sr'] = sr
        if isinstance(polygons, list):
            params['polygons'] = polygons
        elif isinstance(polygons, Polygon):
            params['polygons'] = [polygons]
        if isinstance(polylines, Polyline):
            params['polylines'] = [polylines]
        elif isinstance(polylines, list):
            params['polylines'] = polylines
        result = self._con.post(path=url, postdata=params)
        if 'error' in result:
            return result
        return self._process_results(result)
    #----------------------------------------------------------------------
    def buffer(self,
               geometries,
               inSR,
               distances,
               unit,
               outSR=None,
               bufferSR=None,
               unionResults=True,
               geodesic=True
               ):
        """
           The buffer operation is performed on a geometry service resource
           The result of this operation is buffered polygons at the
           specified distances for the input geometry array. Options are
           available to union buffers and to use geodesic distance.

           Inputs:
             geometries - The array of geometries to be buffered.
             isSR - The well-known ID of the spatial reference or a spatial
              reference JSON object for the input geometries.
             distances - The distances that each of the input geometries is
              buffered.
             unit - The units for calculating each buffer distance. If unit
              is not specified, the units are derived from bufferSR. If
              bufferSR is not specified, the units are derived from inSR.
             outSR - The well-known ID of the spatial reference or a
              spatial reference JSON object for the input geometries.
             bufferSR - The well-known ID of the spatial reference or a
              spatial reference JSON object for the input geometries.
             unionResults -  If true, all geometries buffered at a given
              distance are unioned into a single (possibly multipart)
              polygon, and the unioned geometry is placed in the output
              array. The default is false
             geodesic - Set geodesic to true to buffer the input geometries
              using geodesic distance. Geodesic distance is the shortest
              path between two points along the ellipsoid of the earth. If
              geodesic is set to false, the 2D Euclidean distance is used
              to buffer the input geometries. The default value depends on
              the geometry type, unit and bufferSR.
        """
        url = self._url + "/buffer"
        params = {
            "f" : "json",
            "inSR" : inSR,
            "geodesic" : json.dumps(geodesic),
            "unionResults" : json.dumps(unionResults)
        }
        if isinstance(geometries, list) and len(geometries) > 0:
            g = geometries[0]
            if isinstance(g, Polygon):
                params['geometries'] = {"geometryType": "esriGeometryPolygon",
                                        "geometries" : self.__geomToStringArray(geometries, "list")}
            elif isinstance(g, Point):
                params['geometries'] = {"geometryType": "esriGeometryPoint",
                                        "geometries" : self.__geomToStringArray(geometries, "list")}
            elif isinstance(g, Polyline):
                params['geometries'] = {"geometryType": "esriGeometryPolyline",
                                                        "geometries" : self.__geomToStringArray(geometries, "list")}
        elif isinstance(geometries, list) and len(geometries) > 0 and \
             isinstance(geometries[0], dict):
            params['geometries'] = geometries
        else:
            return None
        if isinstance(distances, list):
            distances = [str(d) for d in distances]

            params['distances'] = ",".join(distances)
        else:
            params['distances'] = str(distances)
        params['unit'] = unit
        if bufferSR is not None:
            params['bufferSR'] = bufferSR
        if outSR is not None:
            params['outSR'] = outSR

        results = self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def convex_hull(self,
                   geometries,
                   sr=None):
        """
        The convexHull operation is performed on a geometry service
        resource. It returns the convex hull of the input geometry. The
        input geometry can be a point, multipoint, polyline, or polygon.
        The convex hull is typically a polygon but can also be a polyline
        or point in degenerate cases.

        Inputs:
           geometries - The geometries whose convex hull is to be created.
           sr - The well-known ID or a spatial reference JSON object for
                the output geometry.
        """
        url = self._url + "/convexHull"
        params = {
            "f" : "json"
        }
        if isinstance(geometries, list) and len(geometries) > 0:
            g = geometries[0]
            if sr is not None:
                params['sr'] = sr
            else:
                params['sr'] = g.spatialreference
            if isinstance(g, Polygon):
                params['geometries'] = {"geometryType": "esriGeometryPolygon",
                                        "geometries" : self.__geomToStringArray(geometries, "list")}
            elif isinstance(g, Point):
                params['geometries'] = {"geometryType": "esriGeometryPoint",
                                        "geometries" : self.__geomToStringArray(geometries, "list")}
            elif isinstance(g, Polyline):
                params['geometries'] = {"geometryType": "esriGeometryPolyline",
                                                        "geometries" : self.__geomToStringArray(geometries, "list")}
        else:
            return None
        results = self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def cut(self,
            cutter,
            target,
            sr=None):
        """
        The cut operation is performed on a geometry service resource. This
        operation splits the target polyline or polygon where it's crossed
        by the cutter polyline.
        At 10.1 and later, this operation calls simplify on the input
        cutter and target geometries.

        Inputs:
           cutter - The polyline that will be used to divide the target
            into pieces where it crosses the target.The spatial reference
            of the polylines is specified by sr. The structure of the
            polyline is the same as the structure of the JSON polyline
            objects returned by the ArcGIS REST API.
           target - The array of polylines/polygons to be cut. The
            structure of the geometry is the same as the structure of the
            JSON geometry objects returned by the ArcGIS REST API. The
            spatial reference of the target geometry array is specified by
            sr.
           sr - The well-known ID or a spatial reference JSON object for
            the output geometry.
        """
        url = self._url + "/cut"
        params = {
            "f" : "json"
        }
        if sr is not None:
            params['sr'] = sr
        if isinstance(cutter, (Polyline, dict)):
            params['cutter'] = cutter
        else:
            raise AttributeError("Input must be type Polyline/Dictionary")
        if isinstance(target, list) and len(target) > 0:
            template = {"geometryType": "",
                        "geometries" : []}
            for g in target:
                if isinstance(g, Polygon):
                    template['geometryType'] = "esriGeometryPolygon"
                    template['geometries'].append(g)
                if isinstance(g, Polyline):
                    template['geometryType'] = "esriGeometryPolyline"
                    template['geometries'].append(g)
                else:
                    AttributeError("Invalid geometry in target, entries can only be Polygon or Polyline")
                del g
            params['target'] = template
        else:
            AttributeError("You must provide at least 1 Polygon/Polyline geometry in a list")
        results = self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def density(self,
                geometries,
                sr,
                maxSegmentLength,
                lengthUnit,
                geodesic=False,
                ):
        """
        The densify operation is performed on a geometry service resource.
        This operation densifies geometries by plotting points between
        existing vertices.

        Inputs:
           geometries - The array of geometries to be densified. The
            structure of each geometry in the array is the same as the
            structure of the JSON geometry objects returned by the ArcGIS
            REST API.
           sr - The well-known ID or a spatial reference JSON object for
            the input polylines. For a list of valid WKID values, see
            Projected coordinate systems and Geographic coordinate systems.
           maxSegmentLength - All segments longer than maxSegmentLength are
            replaced with sequences of lines no longer than
            maxSegmentLength.
           lengthUnit - The length unit of maxSegmentLength. If geodesic is
            set to false, then the units are derived from sr, and
            lengthUnit is ignored. If geodesic is set to true, then
            lengthUnit must be a linear unit. In a case where lengthUnit is
            not specified and sr is a PCS, the units are derived from sr.
            In a case where lengthUnit is not specified and sr is a GCS,
            then the units are meters.
           geodesic - If geodesic is set to true, then geodesic distance is
            used to calculate maxSegmentLength. Geodesic distance is the
            shortest path between two points along the ellipsoid of the
            earth. If geodesic is set to false, then 2D Euclidean distance
            is used to calculate maxSegmentLength. The default is false.
        """
        url = self._url + "/densify"
        template = {"geometryType": None,
                    "geometries" : []}
        params = {
            "f" : "json",
            "sr" : sr,
            "maxSegmentLength" : maxSegmentLength,
            "lengthUnit" : lengthUnit,
            "geodesic" : geodesic
        }
        if isinstance(geometries, list) and len(geometries) > 0:
            for g in geometries:
                g = Geometry(g)
                if isinstance(g, Polyline):
                    template['geometryType'] = "esriGeometryPolyline"
                elif isinstance(g, Polygon):
                    template['geometryType'] = "esriGeometryPolygon"
                else:
                    raise AttributeError("Invalid geometry type")

                template['geometries'].append(g)

        elif isinstance(geometries, dict):
            g = Geometry(geometries)
            if isinstance(g, Polyline):
                template['geometryType'] = "esriGeometryPolyline"
            elif isinstance(g, Polygon):
                template['geometryType'] = "esriGeometryPolygon"
            template['geometries'].append(g)
        params['geometries'] = template
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def difference(self,
                   geometries,
                   sr,
                   geometry
                   ):
        """
        The difference operation is performed on a geometry service
        resource. This operation constructs the set-theoretic difference
        between each element of an array of geometries and another geometry
        the so-called difference geometry. In other words, let B be the
        difference geometry. For each geometry, A, in the input geometry
        array, it constructs A-B.

        Inputs:
          geometries -  An array of points, multipoints, polylines or
           polygons. The structure of each geometry in the array is the
           same as the structure of the JSON geometry objects returned by
           the ArcGIS REST API.
          geometry - A single geometry of any type and of a dimension equal
           to or greater than the elements of geometries. The structure of
           geometry is the same as the structure of the JSON geometry
           objects returned by the ArcGIS REST API. The use of simple
           syntax is not supported.
          sr - The well-known ID of the spatial reference or a spatial
           reference JSON object for the input geometries.
        """
        url = self._url + "/difference"
        params = {
            "f" : "json",
            "sr" : sr

        }
        if isinstance(geometries, list) and len(geometries) > 0:
            template = {"geometryType": None,
                        "geometries" : []}
            for g in geometries:
                if isinstance(g, Polyline):
                    template['geometryType'] = "esriGeometryPolyline"
                elif isinstance(g, Polygon):
                    template['geometryType'] = "esriGeometryPolygon"
                elif isinstance(g, Point):
                    template['geometryType'] = "esriGeometryPoint"
                elif isinstance(g, Point):
                    template['geometryType'] = "esriGeometryMultipoint"
                else:
                    raise AttributeError("Invalid geometry type")
                template['geometries'].append(g)
                del g
            params['geometries'] = template
        geomTemplate = {"geometryType": None,
                        "geometries" : []
                        }
        if isinstance(geometry, Polyline):
            geomTemplate['geometryType'] = "esriGeometryPolyline"
        elif isinstance(geometry, Polygon):
            geomTemplate['geometryType'] = "esriGeometryPolygon"
        elif isinstance(geometry, Point):
            geomTemplate['geometryType'] = "esriGeometryPoint"
        elif isinstance(geometry, Point):
            geomTemplate['geometryType'] = "esriGeometryMultipoint"
        else:
            raise AttributeError("Invalid geometry type")
        geomTemplate['geometry'] = geometry
        params['geometry'] = geomTemplate
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def distance(self,
                 sr,
                 geometry1,
                 geometry2,
                 distanceUnit="",
                 geodesic=False
                 ):
        """
        The distance operation is performed on a geometry service resource.
        It reports the 2D Euclidean or geodesic distance between the two
        geometries.

        Inputs:
         sr - The well-known ID or a spatial reference JSON object for
          input geometries.
         geometry1 - The geometry from which the distance is to be
          measured. The structure of the geometry is same as the structure
          of the JSON geometry objects returned by the ArcGIS REST API.
         geometry2 - The geometry from which the distance is to be
          measured. The structure of the geometry is same as the structure
          of the JSON geometry objects returned by the ArcGIS REST API.
         distanceUnit - specifies the units for measuring distance between
          the geometry1 and geometry2 geometries.
         geodesic - If geodesic is set to true, then the geodesic distance
          between the geometry1 and geometry2 geometries is returned.
          Geodesic distance is the shortest path between two points along
          the ellipsoid of the earth. If geodesic is set to false or not
          specified, the planar distance is returned. The default value is
          false.
        """
        url = self._url + "/distance"
        params = {
            "f" : "json",
            "sr" : sr,
            "distanceUnit" : distanceUnit,
            "geodesic" : geodesic
        }
        geometry1 = self.__geometryToGeomTemplate(geometry=geometry1)
        geometry2 = self.__geometryToGeomTemplate(geometry=geometry2)
        params['geometry1'] = geometry1
        params['geometry2'] = geometry2
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def find_transformation(self, inSR, outSR, extentOfInterest=None, numOfResults=1):
        """
        The findTransformations operation is performed on a geometry
        service resource. This operation returns a list of applicable
        geographic transformations you should use when projecting
        geometries from the input spatial reference to the output spatial
        reference. The transformations are in JSON format and are returned
        in order of most applicable to least applicable. Recall that a
        geographic transformation is not needed when the input and output
        spatial references have the same underlying geographic coordinate
        systems. In this case, findTransformations returns an empty list.
        Every returned geographic transformation is a forward
        transformation meaning that it can be used as-is to project from
        the input spatial reference to the output spatial reference. In the
        case where a predefined transformation needs to be applied in the
        reverse direction, it is returned as a forward composite
        transformation containing one transformation and a transformForward
        element with a value of false.

        Inputs:
           inSR - The well-known ID (WKID) of the spatial reference or a
             spatial reference JSON object for the input geometries
           outSR - The well-known ID (WKID) of the spatial reference or a
             spatial reference JSON object for the input geometries
           extentOfInterest -  The bounding box of the area of interest
             specified as a JSON envelope. If provided, the extent of
             interest is used to return the most applicable geographic
             transformations for the area. If a spatial reference is not
             included in the JSON envelope, the inSR is used for the
             envelope.
           numOfResults - The number of geographic transformations to
             return. The default value is 1. If numOfResults has a value of
             -1, all applicable transformations are returned.
        """
        params = {
            "f" : "json",
            "inSR" : inSR,
            "outSR" : outSR
        }
        url = self._url + "/findTransformations"
        if isinstance(numOfResults, int):
            params['numOfResults'] = numOfResults
        if isinstance(extentOfInterest, Envelope):
            params['extentOfInterest'] = extentOfInterest
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def from_geo_coordinate_string(self, sr, strings,
                                conversionType, conversionMode=None):
        """
        The from_geo_coordinate_string operation is performed on a geometry
        service resource. The operation converts an array of well-known
        strings into xy-coordinates based on the conversion type and
        spatial reference supplied by the user. An optional conversion mode
        parameter is available for some conversion types.

        Inputs:
         sr - The well-known ID of the spatial reference or a spatial
          reference json object.
         strings - An array of strings formatted as specified by
          conversionType.
          Syntax: [<string1>,...,<stringN>]
          Example: ["01N AA 66021 00000","11S NT 00000 62155",
                    "31U BT 94071 65288"]
         conversionType - The conversion type of the input strings.
          Valid conversion types are:
           MGRS - Military Grid Reference System
           USNG - United States National Grid
           UTM - Universal Transverse Mercator
           GeoRef - World Geographic Reference System
           GARS - Global Area Reference System
           DMS - Degree Minute Second
           DDM - Degree Decimal Minute
           DD - Decimal Degree
         conversionMode - Conversion options for MGRS, UTM and GARS
          conversion types.
          Conversion options for MGRS and UTM conversion types.
          Valid conversion modes for MGRS are:
           mgrsDefault - Default. Uses the spheroid from the given spatial
            reference.
           mgrsNewStyle - Treats all spheroids as new, like WGS 1984. The
            180 degree longitude falls into Zone 60.
           mgrsOldStyle - Treats all spheroids as old, like Bessel 1841.
            The 180 degree longitude falls into Zone 60.
           mgrsNewWith180InZone01 - Same as mgrsNewStyle except the 180
            degree longitude falls into Zone 01.
           mgrsOldWith180InZone01 - Same as mgrsOldStyle except the 180
            degree longitude falls into Zone 01.
          Valid conversion modes for UTM are:
           utmDefault - Default. No options.
           utmNorthSouth - Uses north/south latitude indicators instead of
            zone numbers. Non-standard. Default is recommended
        """
        url = self._url + "/fromGeoCoordinateString"
        params = {
            "f" : "json",
            "sr" : sr,
            "strings" : strings,
            "conversionType" : conversionType
        }
        if not conversionMode is None:
            params['conversionMode'] = conversionMode
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def generalize(self,
                   sr,
                   geometries,
                   maxDeviation,
                   deviationUnit):
        """
        The generalize operation is performed on a geometry service
        resource. The generalize operation simplifies the input geometries
        using the Douglas-Peucker algorithm with a specified maximum
        deviation distance. The output geometries will contain a subset of
        the original input vertices.

        Inputs:
         sr - The well-known ID or a spatial reference JSON object for the
          input geometries.
         geometries - The array of geometries to be generalized.
         maxDeviation - maxDeviation sets the maximum allowable offset,
          which will determine the degree of simplification. This value
          limits the distance the output geometry can differ from the input
          geometry.
         deviationUnit - A unit for maximum deviation. If a unit is not
          specified, the units are derived from sr.
        """
        url = self._url + "/generalize"
        params = {
            "f" : "json",
            "sr" : sr,
            "deviationUnit" : deviationUnit,
            "maxDeviation": maxDeviation
        }
        params['geometries'] = self.__geometryListToGeomTemplate(geometries=geometries)
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def intersect(self,
                  sr,
                  geometries,
                  geometry
                  ):
        """
        The intersect operation is performed on a geometry service
        resource. This operation constructs the set-theoretic intersection
        between an array of geometries and another geometry. The dimension
        of each resultant geometry is the minimum dimension of the input
        geometry in the geometries array and the other geometry specified
        by the geometry parameter.

        Inputs:
         sr - The well-known ID or a spatial reference JSON object for the
          input geometries.
         geometries - An array of points, multipoints, polylines, or
          polygons. The structure of each geometry in the array is the same
          as the structure of the JSON geometry objects returned by the
          ArcGIS REST API.
         geometry - A single geometry of any type with a dimension equal to
          or greater than the elements of geometries.
        """
        url = self._url + "/intersect"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries" : self.__geometryListToGeomTemplate(geometries=geometries),
            "geometry" : self.__geometryToGeomTemplate(geometry=geometry)
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def label_points(self,
                    sr,
                    polygons,
                    ):
        """
        The label_points operation is performed on a geometry service
        resource. The labelPoints operation calculates an interior point
        for each polygon specified in the input array. These interior
        points can be used by clients for labeling the polygons.

        Inputs:
         sr - The well-known ID of the spatial reference or a spatial
          reference JSON object for the input polygons.
         polygons - The array of polygons whose label points are to be
          computed. The spatial reference of the polygons is specified by
          sr.
        """
        url = self._url + "/labelPoints"
        params = {
            "f" : "json",
            "sr" : sr,
            "polygons": self.__geomToStringArray(geometries=polygons,
                                                 returnType="list")
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return results
    #----------------------------------------------------------------------
    def lengths(self,
                sr,
                polylines,
                lengthUnit,
                calculationType
                ):
        """
        The lengths operation is performed on a geometry service resource.
        This operation calculates the 2D Euclidean or geodesic lengths of
        each polyline specified in the input array.

        Inputs:
         sr - The well-known ID of the spatial reference or a spatial
          reference JSON object for the input polylines.
         polylines - The array of polylines whose lengths are to be
          computed.
         lengthUnit - The unit in which lengths of polylines will be
          calculated. If calculationType is planar, then lengthUnit can be
          any esriUnits constant. If calculationType is planar and
          lengthUnit is not specified, then the units are derived from sr.
          If calculationType is not planar, then lengthUnit must be a
          linear esriUnits constant such as esriSRUnit_Meter or
          esriSRUnit_SurveyMile. If calculationType is not planar and
          lengthUnit is not specified, then the units are meters.
         calculationType - calculationType defines the length calculation
          for the geometry. The type can be one of the following values:
            planar - Planar measurements use 2D Euclidean distance to
             calculate length. This type should only be used if the length
             needs to be calculated in the given spatial reference.
             Otherwise, use preserveShape.
            geodesic - Use this type if you want to calculate a length
             using only the vertices of the polygon and define the lines
             between the vertices as geodesic segments independent of the
             actual shape of the polyline. A geodesic segment is the
             shortest path between two points on an earth ellipsoid.
            preserveShape - This type calculates the length of the geometry
             on the surface of the earth ellipsoid. The shape of the
             geometry in its coordinate system is preserved.
        """
        allowedCalcTypes = ['planar', 'geodesic', 'preserveShape']
        if calculationType not in allowedCalcTypes:
            raise AttributeError("Invalid calculation Type")
        url = self._url + "/lengths"
        params = {
            "f" : "json",
            "sr" : sr,
            "polylines": self.__geomToStringArray(geometries=polylines,
                                                 returnType="list"),
            "lengthUnit" : lengthUnit,
            "calculationType" : calculationType
        }
        res = self._con.post(path=url, postdata=params)
        if res is not None and 'lengths' in res:
            return res['lengths']
        else:
            return res
    #----------------------------------------------------------------------
    def offset(self,
               geometries,
               offsetDistance,
               offsetUnit,
               offsetHow="esriGeometryOffsetRounded",
               bevelRatio=10,
               simplifyResult=False,
               sr=None,
               ):
        """
        The offset operation is performed on a geometry service resource.
        This operation constructs geometries that are offset from the
        given input geometries. If the offset parameter is positive, the
        constructed offset will be on the right side of the geometry. Left
        side offsets are constructed with negative parameters. Tracing the
        geometry from its first vertex to the last will give you a
        direction along the geometry. It is to the right and left
        perspective of this direction that the positive and negative
        parameters will dictate where the offset is constructed. In these
        terms, it is simple to infer where the offset of even horizontal
        geometries will be constructed.

        Inputs:
         geometries -  The array of geometries to be offset.
         offsetDistance - Specifies the distance for constructing an offset
          based on the input geometries. If the offsetDistance parameter is
          positive, the constructed offset will be on the right side of the
          curve. Left-side offsets are constructed with negative values.
         offsetUnit - A unit for offset distance. If a unit is not
          specified, the units are derived from sr.
         offsetHow - The offsetHow parameter determines how outer corners
          between segments are handled. The three options are as follows:
           esriGeometryOffsetRounded - Rounds the corner between extended
            offsets.
           esriGeometryOffsetBevelled - Squares off the corner after a
            given ratio distance.
           esriGeometryOffsetMitered - Attempts to allow extended offsets
            to naturally intersect, but if that intersection occurs too far
            from the corner, the corner is eventually bevelled off at a
            fixed distance.
         bevelRatio - bevelRatio is multiplied by the offset distance, and
          the result determines how far a mitered offset intersection can
          be located before it is bevelled. When mitered is specified,
          bevelRatio is ignored and 10 is used internally. When bevelled is
          specified, 1.1 will be used if bevelRatio is not specified.
          bevelRatio is ignored for rounded offset.
         simplifyResult - if simplifyResult is set to true, then self
          intersecting loops will be removed from the result offset
          geometries. The default is false.
         sr - The well-known ID or a spatial reference JSON object for the
          input geometries.
        """
        allowedHow = ["esriGeometryOffsetRounded",
                      "esriGeometryOffsetBevelled",
                      "esriGeometryOffsetMitered"]
        if offsetHow not in allowedHow:
            raise AttributeError("Invalid Offset How value")
        url = self._url + "/offset"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries": self.__geometryListToGeomTemplate(geometries=geometries),
            "offsetDistance": offsetDistance,
            "offsetUnit" : offsetUnit,
            "offsetHow" : offsetHow,
            "bevelRatio" : bevelRatio,
            "simplifyResult" : json.dumps(simplifyResult)
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def project(self,
                geometries,
                inSR,
                outSR,
                transformation="",
                transformFoward=False):
        """
        The project operation is performed on a geometry service resource.
        This operation projects an array of input geometries from the input
        spatial reference to the output spatial reference.

        Inputs:
         geometries - The array of geometries to be projected.
         inSR - The well-known ID (WKID) of the spatial reference or a
          spatial reference JSON object for the input geometries.
         outSR - The well-known ID (WKID) of the spatial reference or a
          spatial reference JSON object for the input geometries.
         transformation - The WKID or a JSON object specifying the
          geographic transformation (also known as datum transformation) to
          be applied to the projected geometries. Note that a
          transformation is needed only if the output spatial reference
          contains a different geographic coordinate system than the input
          spatial reference.
         transformForward - A Boolean value indicating whether or not to
          transform forward. The forward or reverse direction of
          transformation is implied in the name of the transformation. If
          transformation is specified, a value for the transformForward
          parameter must also be specified. The default value is false.
        """
        url = self._url + "/project"
        params = {
            "f" : "json",
            "inSR" : inSR,
            "geometries": self.__geometryListToGeomTemplate(geometries=geometries),
            "outSR" : outSR,
            "transformation" : transformation,
            "transformFoward": transformFoward
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def relation(self,
                 geometries1,
                 geometries2,
                 sr,
                 relation="esriGeometryRelationIntersection",
                 relationParam=""):
        """
        The relation operation is performed on a geometry service resource.
        This operation determines the pairs of geometries from the input
        geometry arrays that participate in the specified spatial relation.
        Both arrays are assumed to be in the spatial reference specified by
        sr, which is a required parameter. Geometry types cannot be mixed
        within an array. The relations are evaluated in 2D. In other words,
        z coordinates are not used.

        Inputs:
         geometries1 - The first array of geometries used to compute the
          relations.
         geometries2 -The second array of geometries used to compute the
         relations.
         sr - The well-known ID of the spatial reference or a spatial
          reference JSON object for the input geometries.
         relation - The spatial relationship to be tested between the two
          input geometry arrays.
          Values: esriGeometryRelationCross | esriGeometryRelationDisjoint |
          esriGeometryRelationIn | esriGeometryRelationInteriorIntersection |
          esriGeometryRelationIntersection | esriGeometryRelationLineCoincidence |
          esriGeometryRelationLineTouch | esriGeometryRelationOverlap |
          esriGeometryRelationPointTouch | esriGeometryRelationTouch |
          esriGeometryRelationWithin | esriGeometryRelationRelation
         relationParam - The Shape Comparison Language string to be
          evaluated.
        """
        relationType = [
            "esriGeometryRelationCross",
            "esriGeometryRelationDisjoint",
            "esriGeometryRelationIn",
            "esriGeometryRelationInteriorIntersection",
            "esriGeometryRelationIntersection",
            "esriGeometryRelationLineCoincidence",
            "esriGeometryRelationLineTouch",
            "esriGeometryRelationOverlap",
            "esriGeometryRelationPointTouch",
            "esriGeometryRelationTouch",
            "esriGeometryRelationWithin",
            "esriGeometryRelationRelation"
        ]
        if relation not in relationType:
            raise AttributeError("Invalid relation type")
        url = self._url + "/relation"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries1": self.__geometryListToGeomTemplate(geometries=geometries1),
            "geometries2": self.__geometryListToGeomTemplate(geometries=geometries2),
            "relation" : relation,
            "relationParam" : relationParam
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def reshape(self,
                sr,
                target,
                reshaper
                ):
        """
        The reshape operation is performed on a geometry service resource.
        It reshapes a polyline or polygon feature by constructing a
        polyline over the feature. The feature takes the shape of the
        reshaper polyline from the first place the reshaper intersects the
        feature to the last.

        Input:
         sr - The well-known ID of the spatial reference or a spatial
          reference JSON object for the input geometries.
         target -  The polyline or polygon to be reshaped.
         reshaper - The single-part polyline that does the reshaping.
        """
        url = self._url + "/reshape"
        params = {
            "f" : "json",
            "sr" : sr,
            "target" : self.__geometryToGeomTemplate(geometry=target)
        }
        if isinstance(reshaper, Polyline):
            params["reshaper"] = reshaper
        elif isinstance(reshaper, dict):
            params['reshaper'] = reshaper
        else:
            raise AttributeError("Invalid reshaper object, must be Polyline")
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def simplify(self,
                 sr,
                 geometries
                 ):
        """
        The simplify operation is performed on a geometry service resource.
        Simplify permanently alters the input geometry so that the geometry
        becomes topologically consistent. This resource applies the ArcGIS
        simplify operation to each geometry in the input array.

        Inputs:
        sr - The well-known ID of the spatial reference or a spatial
          reference JSON object for the input geometries.
        geometries - The array of geometries to be simplified.
        """
        url = self._url + "/simplify"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries" : self.__geometryListToGeomTemplate(geometries=geometries)
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def to_geo_coordinate_string(self,
                              sr,
                              coordinates,
                              conversionType,
                              conversionMode="mgrsDefault",
                              numOfDigits=None,
                              rounding=True,
                              addSpaces=True
                              ):
        """
        The toGeoCoordinateString operation is performed on a geometry
        service resource. The operation converts an array of
        xy-coordinates into well-known strings based on the conversion type
        and spatial reference supplied by the user. Optional parameters are
        available for some conversion types. Note that if an optional
        parameter is not applicable for a particular conversion type, but a
        value is supplied for that parameter, the value will be ignored.

        Inputs:
          sr -  The well-known ID of the spatial reference or a spatial
           reference json object.
          coordinates - An array of xy-coordinates in JSON format to be
           converted. Syntax: [[x1,y2],...[xN,yN]]
          conversionType - The conversion type of the input strings.
           Allowed Values:
            MGRS - Military Grid Reference System
            USNG - United States National Grid
            UTM - Universal Transverse Mercator
            GeoRef - World Geographic Reference System
            GARS - Global Area Reference System
            DMS - Degree Minute Second
            DDM - Degree Decimal Minute
            DD - Decimal Degree
          conversionMode - Conversion options for MGRS and UTM conversion
           types.
           Valid conversion modes for MGRS are:
            mgrsDefault - Default. Uses the spheroid from the given spatial
             reference.
            mgrsNewStyle - Treats all spheroids as new, like WGS 1984. The
             180 degree longitude falls into Zone 60.
            mgrsOldStyle - Treats all spheroids as old, like Bessel 1841.
             The 180 degree longitude falls into Zone 60.
            mgrsNewWith180InZone01 - Same as mgrsNewStyle except the 180
             degree longitude falls into Zone 01.
            mgrsOldWith180InZone01 - Same as mgrsOldStyle except the 180
             degree longitude falls into Zone 01.
           Valid conversion modes for UTM are:
            utmDefault - Default. No options.
            utmNorthSouth - Uses north/south latitude indicators instead of
             zone numbers. Non-standard. Default is recommended.
          numOfDigits - The number of digits to output for each of the
           numerical portions in the string. The default value for
           numOfDigits varies depending on conversionType.
          rounding - If true, then numeric portions of the string are
           rounded to the nearest whole magnitude as specified by
           numOfDigits. Otherwise, numeric portions of the string are
           truncated. The rounding parameter applies only to conversion
           types MGRS, USNG and GeoRef. The default value is true.
          addSpaces - If true, then spaces are added between components of
           the string. The addSpaces parameter applies only to conversion
           types MGRS, USNG and UTM. The default value for MGRS is false,
           while the default value for both USNG and UTM is true.
        """
        params = {
            "f": "json",
            "sr" : sr,
            "coordinates" : coordinates,
            "conversionType": conversionType
        }
        url = self._url + "/toGeoCoordinateString"
        if not conversionMode is None:
            params['conversionMode'] = conversionMode
        if isinstance(numOfDigits, int):
            params['numOfDigits'] = numOfDigits
        if isinstance(rounding, int):
            params['rounding'] = rounding
        if isinstance(addSpaces, bool):
            params['addSpaces'] = addSpaces
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def trim_extend(self,
                   sr,
                   polylines,
                   trimExtendTo,
                   extendHow=0):
        """
        The trim_extend operation is performed on a geometry service
        resource. This operation trims or extends each polyline specified
        in the input array, using the user-specified guide polylines. When
        trimming features, the part to the left of the oriented cutting
        line is preserved in the output, and the other part is discarded.
        An empty polyline is added to the output array if the corresponding
        input polyline is neither cut nor extended.

        Inputs:
         sr - The well-known ID of the spatial reference or a spatial
           reference json object.
         polylines - An array of polylines to be trimmed or extended.
         trimExtendTo - A polyline that is used as a guide for trimming or
          extending input polylines.
         extendHow - A flag that is used along with the trimExtend
          operation.
          0 - By default, an extension considers both ends of a path. The
           old ends remain, and new points are added to the extended ends.
           The new points have attributes that are extrapolated from
           adjacent existing segments.
          1 - If an extension is performed at an end, relocate the end
           point to the new position instead of leaving the old point and
           adding a new point at the new position.
          2 - If an extension is performed at an end, do not extrapolate
           the end-segment's attributes for the new point. Instead, make
           its attributes the same as the current end. Incompatible with
           esriNoAttributes.
          4 - If an extension is performed at an end, do not extrapolate
           the end-segment's attributes for the new point. Instead, make
           its attributes empty. Incompatible with esriKeepAttributes.
          8 - Do not extend the 'from' end of any path.
          16 - Do not extend the 'to' end of any path.
        """
        allowedHow = [0,1,2,4,8,16]
        if extendHow not in allowedHow:
            raise AttributeError("Invalid extend How value.")
        url = self._url + "/trimExtend"
        params = {
            "f" : "json",
            "sr" : sr,
            "polylines" : self.__geomToStringArray(geometries=polylines, returnType="list"),
            "extendHow": extendHow,
            "trimExtendTo" : trimExtendTo
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
    #----------------------------------------------------------------------
    def union(self,
              sr,
              geometries):
        """
        The union operation is performed on a geometry service resource.
        This operation constructs the set-theoretic union of the geometries
        in the input array. All inputs must be of the same type.

        Inputs:
        sr - The well-known ID of the spatial reference or a spatial
         reference json object.
        geometries - The array of geometries to be unioned.
        """
        url = self._url + "/union"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries" : self.__geometryListToGeomTemplate(geometries=geometries)
        }
        results =  self._con.post(path=url, postdata=params)
        if 'error' in results:
            return results
        return self._process_results(results)
