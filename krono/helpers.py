import datetime
import os

def clear():
    os.system("clear")

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def datetime_to_string(dt):
    return dt.strftime(DATETIME_FORMAT)

def string_to_datetime(string):
    return datetime.strptime(string, DATETIME_FORMAT)
