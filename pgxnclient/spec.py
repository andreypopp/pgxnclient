"""
pgxnclient -- specification object
"""

# Copyright (C) 2011-2012 Daniele Varrazzo

# This file is part of the PGXN client


import os
import re
import operator as _op
from collections import namedtuple

from pgxnclient.i18n import _
from pgxnclient.errors import BadSpecError, ResourceNotFound

from pgxnclient.utils.semver import SemVer
from pgxnclient.utils.strings import Term

def parse(spec):
    """
    Parse spec.
    """
    if spec.startswith('http://') or spec.startswith('https://'):
        return HTTPSpec(spec)

    if os.sep in spec:
        # This is a local thing, let's see what
        if os.path.isdir(spec):
            return LocalSpec(spec)
        elif os.path.exists(spec):
            return LocalSpec(spec)
        else:
            raise ResourceNotFound(_("cannot find '%s'") % spec)

    # split operator/version and name
    m = re.match(r'(.+?)(?:(==|=|>=|>|<=|<)(.*))?$', spec)
    if m is None:
        raise BadSpecError(
            _("bad format for version specification: '%s'"), spec)

    name = Term(m.group(1))
    op = m.group(2)
    if op == '=':
        op = '=='

    if op is not None:
        ver = SemVer.clean(m.group(3))
    else:
        ver = None

    return Spec(name, op, ver)

class BaseSpec(object):
    """
    Base class for spec.
    """

    # Available release statuses.
    # Order matters.
    UNSTABLE = 0
    TESTING = 1
    STABLE = 2

    STATUS = {
        'unstable': UNSTABLE,
        'testing': TESTING,
        'stable': STABLE, }

    opmap = {'==': _op.eq, '<=': _op.le, '<': _op.lt, '>=': _op.ge, '>': _op.gt}

    def __init__(self, args):
        self.args = args

    def accepted(self, version, _map=None):
        """Return True if the given version is accepted in the spec."""
        return True

class Spec(namedtuple('Spec', ['name', 'op', 'ver']), BaseSpec):

    def accepted(self, version, _map=None):
        _map = _map or self.opmap
        if self.op is None:
            return True
        return _map[self.op](version, self.ver)

class LocalSpec(namedtuple('HTTPSpec', ['url']), BaseSpec):
    pass

class HTTPSpec(namedtuple('HTTPSpec', ['url']), BaseSpec):
    pass
