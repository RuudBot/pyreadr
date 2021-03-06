"""
@author: Otto Fajardo
"""
from collections import OrderedDict
import os

import pandas as pd

from ._pyreadr_parser import PyreadrParser, ListObjectsParser
from ._pyreadr_writer import PyreadrWriter
from .custom_errors import PyreadrError


def read_r(path, use_objects=None, timezone=None):
    """
    Read an R RData or Rds file into pandas data frames

    Parameters
    ----------
        path : str
            path to the file. The string is assumed to be utf-8 encoded.
        use_objects : list, optional
            a list with object names to read from the file. Only those objects will be imported. Case sensitive!
        timezone : str, optional
            timezone to localize datetimes, UTC otherwise.
            R datetimes (POSIXct and POSIXlt) are stored as UTC, but coverted to some timezone (explicitly if set by the
            user or implicitly to local zone) when displaying it in R. librdata cannot recover that timezone information
            therefore timestamps are displayed in UTC, unless this parameter is set.

    Returns
    -------
        result : OrderedDict
            object name as key and pandas data frame as value
    """

    parser = PyreadrParser()
    if use_objects:
        parser.set_use_objects(use_objects)
    if timezone:
        parser.set_timezone(timezone)

    if not isinstance(path, str):
        raise PyreadrError("path must be a string!")
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise PyreadrError("File {0} does not exist!".format(path))
    parser.parse(path)

    result = OrderedDict()
    for table_index, table in enumerate(parser.table_data):
        result[table.name] = table.convert_to_pandas_dataframe()
    return result


def list_objects(path):
    """
    Read an R RData or Rds file and lists objects and their column names.
    Not all objects are readable, and also it is not always possible to read the column names without parsing the
    whole file, in those cases this method will return Nones instead of column names.

    Parameters
    ----------
        path : str
            path to the file. The string is assumed to be utf-8 encoded.

    Returns
    -------
        result : list
            a list of dictionaries, where each dictionary has a key "object_name" with the name of the object and
            columns with a list of columns.
    """

    parser = ListObjectsParser()
    if not isinstance(path, str):
        raise PyreadrError("path must be a string!")
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise PyreadrError("File {0} does not exist!".format(path))
 
    parser.parse(path)
    return parser.object_list
    
    
def write_rdata(path, df, df_name="dataset", dateformat="%Y-%m-%d", datetimeformat="%Y-%m-%d %H:%M:%S"):
    """
    Write a single pandas data frame to a rdata file.

    Parameters
    ----------
        path : str
            path to the file. The string is assumed to be utf-8 encoded.
        df : pandas data frame
            the dataframe to write
        df_name : str
            name for the R dataframe object, cannot be empty string. If 
            not supplied will default to "dataset"
        dateformat : str
            string to format datetime.date objects. 
            By default "%Y-%m-%d".
        datetimeformat : str
            string to format datetime like objects. By default "%Y-%m-%d %H:%M:%S".
    """
    
    if not df_name:
        msg = "df_name must be a valid string"
        raise PyreadrError(msg)
        
    if not isinstance(df, pd.DataFrame):
        msg = "df must be a pandas data frame"
        raise PyreadrError(msg)
    
    file_format = "rdata"
    writer = PyreadrWriter()

    if not isinstance(path, str):
        raise PyreadrError("path must be a string!")
    path = os.path.expanduser(path)

    writer.write_r(path, file_format, df, df_name, dateformat, datetimeformat)


def write_rds(path, df, dateformat="%Y-%m-%d", datetimeformat="%Y-%m-%d %H:%M:%S"):
    """
    Write a single pandas data frame to a rds file.

    Parameters
    ----------
        path : str
            path to the file. The string is assumed to be utf-8 encoded.
        df : pandas data frame
            the dataframe to write
        dateformat : str
            string to format datetime.date objects. 
            By default "%Y-%m-%d".
        datetimeformat : str
            string to format datetime like objects. By default "%Y-%m-%d %H:%M:%S".
    """
    
    if not isinstance(df, pd.DataFrame):
        msg = "df must be a pandas data frame"
        raise PyreadrError(msg)
    
    file_format = "rds"
    df_name = ""   # this is irrelevant in this case, but we need to pass something
    if not isinstance(path, str):
        raise PyreadrError("path must be a string!")
    path = os.path.expanduser(path)

    writer = PyreadrWriter()
    writer.write_r(path, file_format, df, df_name, dateformat, datetimeformat)
