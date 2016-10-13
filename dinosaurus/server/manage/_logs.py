from __future__ import absolute_import
from __future__ import print_function
from ...common._base import BaseServer
from datetime import datetime
import csv
########################################################################
class Log(BaseServer):
    """ Log of a server """
    _url = None
    _con = None
    _json_dict = None
    _operations = None
    _resources = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection class
        """
        super(Log, self).__init__(url=url,
                                  connection=connection,
                                  initialize=initialize)
        self._url = url
        self._con = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def operations(self):
        """ returns the operations """
        if self._operations is None:
            self.init()
        return self._operations
    #----------------------------------------------------------------------
    @property
    def resources(self):
        """ returns the log resources """
        if self._resources is None:
            self.init()
        return self._resources
    #----------------------------------------------------------------------
    def error_reports_counts(self, machine="*"):
        """ This operation counts the number of error reports (crash
            reports) that have been generated on each machine.
            Input:
               machine - name of the machine in the cluster.  * means all
                         machines.  This is default
            Output:
               dictionary with report count and machine name
        """
        params = {
            "f": "json",
            "machine" : machine
        }
        url = self._url + "/countErrorReports"
        return self._con.post(path=url,
                            postdata=params)
    #----------------------------------------------------------------------
    def clean(self):
        """ Deletes all the log files on all server machines in the site.  """
        params = {
            "f" : "json",
        }
        url = "{}/clean".format(self._url)
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def log_settings(self):
        """ returns the current log settings """
        params = {
            "f" : "json"
        }
        url = self._url + "/settings"
        try:
            return self._con.post(path=url,
                                  postdata=params)['settings']
        except:
            return ""
    #----------------------------------------------------------------------
    def edit_settings(self,
                        logLevel="WARNING",
                        logDir=None,
                        maxLogFileAge=90,
                        maxErrorReportsCount=10):
        """
           The log settings are for the entire site.
           Inputs:
             logLevel -  Can be one of [OFF, SEVERE, WARNING, INFO, FINE,
                         VERBOSE, DEBUG].
             logDir - File path to the root of the log directory
             maxLogFileAge - number of days that a server should save a log
                             file.
             maxErrorReportsCount - maximum number of error report files
                                    per machine
        """
        url = self._url + "/settings/edit"
        allowed_levels =  ("OFF", "SEVERE", "WARNING", "INFO", "FINE", "VERBOSE", "DEBUG")
        currentSettings= self.log_settings
        currentSettings["f"] ="json"

        if logLevel.upper() in allowed_levels:
            currentSettings['logLevel'] = logLevel.upper()
        if logDir is not None:
            currentSettings['logDir'] = logDir
        if maxLogFileAge is not None and \
           isinstance(maxLogFileAge, int):
            currentSettings['maxLogFileAge'] = maxLogFileAge
        if maxErrorReportsCount is not None and \
           isinstance(maxErrorReportsCount, int) and\
           maxErrorReportsCount > 0:
            currentSettings['maxErrorReportsCount'] = maxErrorReportsCount
        return self._con.post(path=url,
                              postdata=currentSettings)
    #----------------------------------------------------------------------
    def query(self,
              startTime=None,
              endTime=None,
              sinceServerStart=False,
              level="WARNING",
              services="*",
              machines="*",
              server="*",
              codes=None,
              processIds=None,
              export=False,
              exportType="CSV", #CSV or TAB
              out_path=None
              ):
        """
           The query operation on the logs resource provides a way to
           aggregate, filter, and page through logs across the entire site.
           Inputs:

        """
        if codes is None:
            codes = []
        if processIds is None:
            processIds = []
        allowed_levels = ("SEVERE", "WARNING", "INFO",
                          "FINE", "VERBOSE", "DEBUG")
        qFilter = {
            "services": "*",
            "machines": "*",
            "server" : "*"
        }
        if len(processIds) > 0:
            qFilter['processIds'] = processIds
        if len(codes) > 0:
            qFilter['codes'] = codes
        params = {
            "f" : "json",
            "sinceServerStart" : sinceServerStart,
            "pageSize" : 10000
        }
        url = "{url}/query".format(url=self._url)
        if startTime is not None and \
           isinstance(startTime, datetime):
            params['startTime'] = startTime.strftime("%Y-%m-%dT%H:%M:%S")
        if endTime is not None and \
           isinstance(endTime, datetime):
            params['endTime'] = endTime.strftime("%Y-%m-%dT%H:%M:%S")
        if level.upper() in allowed_levels:
            params['level'] = level
        if server != "*":
            qFilter['server'] = server.split(',')
        if services != "*":
            qFilter['services'] = services.split(',')
        if machines != "*":
            qFilter['machines'] = machines.split(",")
        params['filter'] = qFilter
        if export == True and \
           out_path is not None:

            messages = self._con.post(path=url,
                                      postdata=params)
            with open(name=out_path, mode='wb') as f:
                hasKeys = False
                if exportType == "TAB":
                    csvwriter = csv.writer(f, delimiter='\t')
                else:
                    csvwriter = csv.writer(f)
                for message in messages['logMessages']:
                    if hasKeys == False:
                        csvwriter.writerow(message.keys())
                        hasKeys = True
                    csvwriter.writerow(message.values())
                    del message
            del messages
            return out_path
        else:
            return self._con.post(path=url,
                                  postdata=params)