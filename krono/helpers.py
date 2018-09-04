import datetime
import os

def clear():
    os.system("clear")

datetime_fmt = "%Y-%m-%d %H:%M:%S (%z)"

def datetime_to_string(dt):
    return dt.strftime(datetime_fmt)

def string_to_datetime(string):
    return datetime.strptime(string, datetime_fmt)
