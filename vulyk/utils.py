# -*- coding=utf-8 -*-

import sys
from functools import wraps
from itertools import islice
import httplib

import six
from flask import jsonify, abort


# Soooo lame
def unique(a):
    """
    Returns unique values from the list preserving order of initial list
    """
    seen = set()
    return [seen.add(x) or x for x in a if x not in seen]


def handle_exception_as_json(exc=Exception):
    if isinstance(exc, Exception):
        exc = Exception

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                fn(*args, **kwargs)
                return jsonify({"result": True})
            except exc as e:
                return jsonify({"result": False, "reason": six.text_type(e)})
        return wrapper
    return decorator


def resolve_task_type(type_name, user):
    """
    Looks for `type_name` in TASK_TYPES list

    :type type_name: str | basestring
    :type user: vulyk.models.user.User

    :rtype: vulyk.models.task_types.AbstractTaskType
    """
    from app import TASKS_TYPES as T

    task_type = None

    if not (type_name and type_name in T.keys()):
        abort(httplib.NOT_FOUND)
    elif not user.is_eligible_for(type_name):
        abort(httplib.FORBIDDEN)
    else:
        task_type = T[type_name]

    return task_type


# Borrowed from elasticutils
def chunked(iterable, n):
    """Returns chunks of n length of iterable

    If len(iterable) % n != 0, then the last chunk will have length
    less than n.

    Example:

    >>> chunked([1, 2, 3, 4, 5], 2)
    [(1, 2), (3, 4), (5,)]

    """
    iterable = iter(iterable)
    while 1:
        t = tuple(islice(iterable, n))
        if t:
            yield t
        else:
            return


def get_tb():
    """
    Returns traceback of the latest exception caught in 'except' block

    :return: traceback of the most recent exception
    """
    return sys.exc_info()[2]
