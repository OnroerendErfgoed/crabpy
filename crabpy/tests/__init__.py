# -*- coding: utf-8 -*-


def as_bool(value):
    '''
    Cast a textual value from a config file to a boolean.

    Will convert 'true', 'True', '1', 't', 'T' or 'Yes' to `True`. All other
    values are considered to be `False`.
    '''
    return value in ['true', 'True', '1', 't', 'T', 'Yes']
