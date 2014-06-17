from __future__ import absolute_import, division, print_function

"""
Say 'yes' to types but 'no' to typing!
"""

import textwrap


__version__ = "0.2.0dev"
__author__ = "Hynek Schlawack"
__license__ = "MIT"
__copyright__ = "Copyright 2014 Hynek Schlawack"


def with_cmp(attrs):
    """
    A class decorator that adds comparison methods based on *attrs*.

    Two instances are compared as if the respective values of *attrs* were
    tuples.

    :param attrs: Attributes to work with.
    :type attrs: `list` of native strings
    """
    def attrs_to_tuple(obj):
        """
        Create a tuple of all values of *obj*'s *attrs*.
        """
        return tuple(getattr(obj, a) for a in attrs)

    def eq(self, other):
        if isinstance(other, self.__class__):
            return attrs_to_tuple(self) == attrs_to_tuple(other)
        else:
            return NotImplemented

    def ne(self, other):
        result = eq(self, other)
        if result is NotImplemented:
            return NotImplemented
        else:
            return not result

    def lt(self, other):
        if isinstance(other, self.__class__):
            return attrs_to_tuple(self) < attrs_to_tuple(other)
        else:
            return NotImplemented

    def le(self, other):
        if isinstance(other, self.__class__):
            return attrs_to_tuple(self) <= attrs_to_tuple(other)
        else:
            return NotImplemented

    def gt(self, other):
        if isinstance(other, self.__class__):
            return attrs_to_tuple(self) > attrs_to_tuple(other)
        else:
            return NotImplemented

    def ge(self, other):
        if isinstance(other, self.__class__):
            return attrs_to_tuple(self) >= attrs_to_tuple(other)
        else:
            return NotImplemented

    def hash_(self):
        return hash(attrs_to_tuple(self))

    def wrap(cl):
        cl.__eq__ = eq
        cl.__ne__ = ne
        cl.__lt__ = lt
        cl.__le__ = le
        cl.__gt__ = gt
        cl.__ge__ = ge
        cl.__hash__ = hash_

        return cl
    return wrap


def with_repr(attrs):
    """
    A class decorator that adds a human-friendly ``__repr__`` method that
    returns a sensible representation based on *attrs*.

    :param attrs: Attributes to work with.
    :type attrs: Iterable of native strings.
    """
    def repr_(self):
        return "<{0}({1})>".format(
            self.__class__.__name__,
            ", ".join(a + "=" + repr(getattr(self, a)) for a in attrs)
        )

    def wrap(cl):
        cl.__repr__ = repr_
        return cl

    return wrap


def _make_wrap_init(init):
    def wrap(cl):
        cl.__original_init__ = cl.__init__
        cl.__init__ = init
        return cl
    return wrap


def with_init(attrs, defaults=None):
    """
    A class decorator that wraps the __init__ method of a class and sets
    *attrs* first using keyword arguments.

    :param attrs: Attributes to work with.
    :type attrs: Iterable of native strings.

    :param defaults: Default values if attributes are omitted on instantiation.
    :type defaults: `dict` or `None`
    """
    if defaults is None:
        defaults = {}

    source = textwrap.dedent("""
def init(self, {args_with_defaults}):
    {assignments}
    self.__original_init__({args})
""".format(
    args_with_defaults=", ".join("{attr}=defaults[{attr}]".format(attr=attr) if attr in defaults else "attr" for attr in attrs),
    args=", ".join(attrs),
    assignments="\n    ".join("self.{attr} = {attr}".format(attr=attr) for attr in attrs)
))
    ns = {"defaults": defaults}
    locs = {}
    exec(source, ns, locs)
    init = locs["init"]
    return _make_wrap_init(init)


def attributes(attrs, defaults=None, create_init=True):
    """
    A convenience class decorator that combines :func:`with_cmp`,
    :func:`with_repr`, and optionally :func:`with_init` to avoid code
    duplication.

    :param attrs: Attributes to work with.
    :type attrs: Iterable of native strings.

    :param defaults: Default values if attributes are omitted on instantiation.
    :type defaults: `dict` or `None`

    :param create_init: Also apply :func:`with_init` (default: `True`)
    :type create_init: `bool`
    """
    def wrap(cl):
        cl = with_cmp(attrs)(with_repr(attrs)(cl))
        if create_init is True:
            return with_init(attrs, defaults=defaults)(cl)
        else:
            return cl
    return wrap
