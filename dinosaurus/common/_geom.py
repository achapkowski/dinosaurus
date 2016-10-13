"""
Represents the geometry objects to use with various
ArcGIS Online Services
"""
from __future__ import absolute_import
import json
from ._utils import is_valid

from six import add_metaclass

class GeometryFactory(type):
    """
    Generates a geometry object from a given set of
    JSON (dictionary or iterable)
    """
    def __call__(cls, iterable=None, **kwargs):
        if iterable is None:
            iterable = ()
        if cls is Geometry:
            if len(iterable) > 0:
                if isinstance(iterable, dict):
                    if 'x' in iterable and \
                       'y' in iterable:
                        return Point(iterable=iterable)
                    elif 'xmin' in iterable:
                        return Envelope(iterable)
                    elif 'wkt' in iterable or \
                         'wkid' in iterable:
                        return SpatialReference(iterable)
                    elif 'rings' in iterable:
                        return Polygon(iterable)
                    elif 'paths' in iterable:
                        return Polyline(iterable)
                    elif 'points' in iterable:
                        return MultiPoint(iterable)
            elif len(kwargs) > 0:
                if 'x' in kwargs or \
                   'y' in kwargs:
                    return Point(**kwargs)
                elif 'xmin' in kwargs:
                    return Envelope(iterable, **kwargs)
                elif 'wkt' in kwargs or \
                     'wkid' in kwargs:
                    return SpatialReference(**kwargs)
                elif 'rings' in kwargs:
                    return Polygon(**kwargs)
                elif 'paths' in kwargs:
                    return Polyline(**kwargs)
                elif 'points' in kwargs:
                    return MultiPoint(**kwargs)
        return type.__call__(cls, iterable, **kwargs)

###########################################################################
class BaseGeometry(dict):
    """base geometry class"""
    #----------------------------------------------------------------------
    @property
    def is_valid(self):
        """boolean to see if input  is valid"""
        return is_valid(self)
    #----------------------------------------------------------------------
    def __getattr__(self, name):
        """
        dictionary items to be retrieved like object attributes
        :param name: attribute name
        :type name: str, int
        :return: dictionary value
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    #----------------------------------------------------------------------
    def __setattr__(self, name, value):
        """
        dictionary items to be set like object attributes.
        :param name: key of item to be set
        :type name: str
        :param value: value to set item to
        """

        self[name] = value
    #----------------------------------------------------------------------
    def __delattr__(self, name):
        """
        dictionary items to be deleted like object attributes
        :param name: key of item to be deleted
        :type name: str
        """

        del self[name]
    #----------------------------------------------------------------------
    def __repr__(self):
        """returns object as string"""
        return json.dumps(self)
    #----------------------------------------------------------------------
    __str__ = __repr__
###########################################################################
@add_metaclass(GeometryFactory)
class Geometry(BaseGeometry):
    def __init__(self, iterable=None, **kwargs):
        if iterable is None:
            iterable = ()
        super(Geometry, self).__init__(iterable)
        self.update(kwargs)
###########################################################################
class SpatialReference(Geometry):
    """
    A spatial reference can be defined using a well-known ID (wkid) or
    well-known text (wkt). The default tolerance and resolution values for
    the associated coordinate system are used. The xy and z tolerance
    values are 1 mm or the equivalent in the unit of the coordinate system.
    If the coordinate system uses feet, the tolerance is 0.00328083333 ft.
    The resolution values are 10x smaller or 1/10 the tolerance values.
    Thus, 0.0001 m or 0.0003280833333 ft. For geographic coordinate systems
    using degrees, the equivalent of a mm at the equator is used.
    The well-known ID (WKID) for a given spatial reference can occasionally
    change. For example, the WGS 1984 Web Mercator (Auxiliary Sphere)
    projection was originally assigned WKID 102100, but was later changed
    to 3857. To ensure backward compatibility with older spatial data
    servers, the JSON wkid property will always be the value that was
    originally assigned to an SR when it was created.
    An additional property, latestWkid, identifies the current WKID value
    (as of a given software release) associated with the same spatial
    reference.
    A spatial reference can optionally include a definition for a vertical
    coordinate system (VCS), which is used to interpret the z-values of a
    geometry. A VCS defines units of measure, the location of z = 0, and
    whether the positive vertical direction is up or down. When a vertical
    coordinate system is specified with a WKID, the same caveat as
    mentioned above applies. There are two VCS WKID properties: vcsWkid and
    latestVcsWkid. A VCS WKT can also be embedded in the string value of
    the wkt property. In other words, the WKT syntax can be used to define
    an SR with both horizontal and vertical components in one string. If
    either part of an SR is custom, the entire SR will be serialized with
    only the wkt property.
    Starting at 10.3, Image Service supports image coordinate systems.
    """
    _type = "SPATIALREFERENCE"
    def __init__(self,
                 iterable=None,
                 **kwargs):
        if iterable is None:
            iterable = ()
        super(SpatialReference, self).__init__(iterable)
        self.update(kwargs)
    #----------------------------------------------------------------------
    @property
    def type(self):
        return self._type
###########################################################################
class Envelope(Geometry):
    """
    An envelope is a rectangle defined by a range of values for each
    coordinate and attribute. It also has a spatialReference field. The
    fields for the z and m ranges are optional. An empty envelope has no
    in space and is defined by the presence of an xmin field a null value
    or a "NaN" string.
    """
    _type = "ENVELOPE"
    def __init__(self, iterable=None, **kwargs):
        if iterable is None:
            iterable = ()
        super(Envelope, self).__init__(iterable)
        self.update(kwargs)
    #----------------------------------------------------------------------
    @property
    def type(self):
        return self._type
###########################################################################
class Point(Geometry):
    """
    A point contains x and y fields along with a spatialReference field. A
    point can also contain m and z fields. A point is empty when its x
    field is present and has the value null or the string "NaN". An empty
    point has no location in space.
    """
    _type = "POINT"
    def __init__(self, iterable=None,
                 **kwargs):
        if iterable is None:
            iterable = ()
        super(Point, self).__init__(iterable)
        self.update(kwargs)
    @property
    def type(self):
        return self._type
###########################################################################
class MultiPoint(Geometry):
    """
    A multipoint contains an array of points, along with a spatialReference
    field. A multipoint can also have boolean-valued hasZ and hasM fields.
    These fields control the interpretation of elements of the points
    array. Omitting an hasZ or hasM field is equivalent to setting it to
    false.
    Each element of the points array is itself an array of two, three, or
    four numbers. It will have two elements for 2D points, two or three
    elements for 2D points with Ms, three elements for 3D points, and three
    or four elements for 3D points with Ms. In all cases, the x coordinate
    is at index 0 of a point's array, and the y coordinate is at index 1.
    For 2D points with Ms, the m coordinate, if present, is at index 2. For
    3D points, the Z coordinate is required and is at index 2. For 3D
    points with Ms, the Z coordinate is at index 2, and the M coordinate,
    if present, is at index 3.
    An empty multipoint has a points field with no elements. Empty points
    are ignored.
    """
    _type = "MULTIPOINT"
    def __init__(self, iterable=None,
                 **kwargs):
        if iterable is None:
            iterable = ()
        super(MultiPoint, self).__init__(iterable)
        self.update(kwargs)
    @property
    def type(self):
        return self._type
###########################################################################
class Polyline(Geometry):
    """
    A polyline contains an array of paths or curvePaths and a
    spatialReference. For polylines with curvePaths, see the sections on
    JSON curve object and Polyline with curve. Each path is represented as
    an array of points, and each point in the path is represented as an
    array of numbers. A polyline can also have boolean-valued hasM and hasZ
    fields.
    See the description of multipoints for details on how the point arrays
    are interpreted.
    An empty polyline is represented with an empty array for the paths
    field. Nulls and/or NaNs embedded in an otherwise defined coordinate
    stream for polylines/polygons is a syntax error.
    """
    _type = "POLYLINE"
    def __init__(self, iterable=None,
                 **kwargs):
        if iterable is None:
            iterable = ()
        super(Polyline, self).__init__(iterable)
        self.update(kwargs)
    @property
    def type(self):
        return self._type
###########################################################################
class Polygon(Geometry):
    """
    A polygon contains an array of rings or curveRings and a
    spatialReference. For polygons with curveRings, see the sections on
    JSON curve object and Polygon with curve. Each ring is represented as
    an array of points. The first point of each ring is always the same as
    the last point. Each point in the ring is represented as an array of
    numbers. A polygon can also have boolean-valued hasM and hasZ fields.

    An empty polygon is represented with an empty array for the rings
    field. Nulls and/or NaNs embedded in an otherwise defined coordinate
    stream for polylines/polygons is a syntax error.
    Polygons should be topologically simple. Exterior rings are oriented
    clockwise, while holes are oriented counter-clockwise. Rings can touch
    at a vertex or self-touch at a vertex, but there should be no other
    intersections. Polygons returned by services are topologically simple.
    When drawing a polygon, use the even-odd fill rule. The even-odd fill
    rule will guarantee that the polygon will draw correctly even if the
    ring orientation is not as described above.
    """
    _type = "POLYGON"
    def __init__(self, iterable=None,
                 **kwargs):
        if iterable is None:
            iterable = ()
        super(Polygon, self).__init__(iterable)
        self.update(kwargs)
    @property
    def type(self):
        return self._type


