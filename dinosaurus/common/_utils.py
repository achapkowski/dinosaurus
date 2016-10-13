"""set of common utilities"""
import os
import sys
import time
import uuid
import zipfile
import datetime
import tempfile
from contextlib import contextmanager

import six
import logging 

list_types = (list, tuple)
if sys.version_info.major == 3:
    number_type = (int, float)
else:
    number_type = (int, float, long)
#----------------------------------------------------------------------
def create_uid():
    if six.PY2:
        return uuid.uuid4().get_hex()
    else:
        return uuid.uuid4().hex
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
#----------------------------------------------------------------------
def online_time_to_string(value,timeFormat):
    """
       Converts a timestamp to date/time string
       Inputs:
          value - timestamp as long
          timeFormat - output date/time format
       Output:
          string
    """
    return datetime.datetime.fromtimestamp(value /1000).strftime(timeFormat)
#----------------------------------------------------------------------
def timestamp_to_datetime(timestamp):
    """
       Converts a timestamp to a datetime object
       Inputs:
          timestamp - timestamp value as Long
       output:
          datetime object
    """
    return datetime.datetime.fromtimestamp(timestamp /1000)

#--------------------------------------------------------------------------
def is_valid(value):
    from _geom import Point, Polygon, Polyline, MultiPoint, Envelope
    """checks if the value is valid"""
    if isinstance(value, Point):
        if hasattr(value, 'x') and \
           hasattr(value, 'y') :
            return True
        elif 'x' in value and \
             (value['x'] is None or \
             value['x'] == "NaN"):
            return True
        return False
    elif isinstance(value, Envelope):
        if all(hasattr(value, a) for a in ('xmin', 'ymin',
                                           'xmax', 'ymax')) and \
           all(isinstance(getattr(value,a), number_type) for a in ('xmin', 'ymin',
                                                                   'xmax', 'ymax')):
            return True
        elif hasattr(value, "xmin") and \
           (value.xmin is None or value.xmin == "NaN"):
            return True
        else:
            return False
    elif isinstance(value, (MultiPoint,
                            Polygon,
                            Polyline)):
        if 'paths' in value:
            if len(value['paths']) == 0:
                return True
            else:
                return is_line(coords=value['paths'])
        elif 'rings' in value:
            if len(value['rings']) == 0:
                return True
            else:
                return is_polygon(coords=value['rings'])
        elif 'points' in value:
            if len(value['points']) == 0:
                return True
            else:
                return is_point(coords=value['points'])
        return False
    else:
        return False
    return False
#--------------------------------------------------------------------------
def is_polygon(coords):
    lengths = all(len(elem) >= 4 for elem in coords)
    valid_pts = all(is_line(part) for part in coords)
    isring = all(elem[0] == elem[-1] for elem in coords)
    return lengths and isring and valid_pts
#--------------------------------------------------------------------------
def is_line(coords):
    """
    checks to see if the line has at
    least 2 points in the list
    """
    if isinstance(coords, list_types) and \
       len(coords) > 0: # list of lists
        return all(is_point(elem) for elem in coords)
    else:
        return True
    return False
#--------------------------------------------------------------------------
def is_point(coords):
    """
    checks to see if the point has at
    least 2 coordinates in the list
    """
    if isinstance(coords, (list, tuple)) and \
       len(coords) > 1:
        for coord in coords:
            if isinstance(coord, number_type):
                return all(isinstance(v, number_type) for v in coords) and \
                       len(coords) > 1
            else:
                return is_point(coord)
    return False
###########################################################################
class Error(Exception): pass
#--------------------------------------------------------------------------
@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, 'UTF-8')))
    temp.close()
    yield temp.name
    os.unlink(temp.name)
#--------------------------------------------------------------------------
def _lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    # http://stevenloria.com/lazy-evaluated-properties-in-python/
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property
#--------------------------------------------------------------------------
def _is_shapefile(data):
    if zipfile.is_zipfile(data):
        zf = zipfile.ZipFile(data, 'r')
        namelist = zf.namelist()
        for name in namelist:
            if name.endswith('.shp') or name.endswith('.SHP'):
                return True
    return False
#--------------------------------------------------------------------------
def rot13(s):
    result = ""

    # Loop over characters.
    for v in s:
        # Convert to number with ord.
        c = ord(v)

        # Shift number back or forward.
        if c >= ord('a') and c <= ord('z'):
            if c > ord('m'):
                c -= 13
            else:
                c += 13
        elif c >= ord('A') and c <= ord('Z'):
            if c > ord('M'):
                c -= 13
            else:
                c += 13

        # Append to result.
        result += chr(c)

    # Return transformation.
    return result
#--------------------------------------------------------------------------
def _to_utf8(data):
    """ Converts strings and collections of strings from unicode to utf-8. """
    if isinstance(data, dict):
        return {_to_utf8(key): _to_utf8(value) \
                for key, value in data.items() if value is not None}
    elif isinstance(data, list):
        return [_to_utf8(element) for element in data]
    elif isinstance(data, str):
        return data
    elif isinstance(data, six.text_type):
        return data.encode('utf-8')
    elif isinstance(data, (float, six.integer_types)):
        return data
    else:
        return data
#--------------------------------------------------------------------------
class _DisableLogger():
    def __enter__(self):
       logging.disable(logging.CRITICAL)
    def __exit__(self, a, b, c):
       logging.disable(logging.NOTSET)
