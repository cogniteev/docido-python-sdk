# encoding: utf-8
"""
Provides Python Embedded Domain Specific Languages.
"""
import operator


class kwargsql(object):
    """Query your Python objects with a `kwargs` syntax.

    Syntax looks like the Mongoengine syntax to query documents.

    Keys in the keyword argument specifies:

    - the attribute's location to test
    - the operation to perform, returning either `True` or `False`
      - first operand is the attribute value
      - second operand if the associated key value.

    For instance:
    - foo=42
    - foo__lt=43

    An extra `not` operator can be specified before the operation,
    for instance: foo__not__gt=0

    To access nested attributes, you can use the '__' separator,
    for instance "foo__bar". This syntax allows you to select:
        - an object attribute
        - value associated to a key in a `dict`.

    It is also possible to select an item of a list, by providing
    the position.


    Example:

    >>> d = {
    >>>    'foo': [
    >>>        { 'bar': 'pika' },
    >>>        { 'bar': 42 },
    >>>    ],
    >>> }
    >>> kwargsql.and_(d, foo__1__bar_gt=41, foo__size=2)
    True
    >>>

    Available operators are as follows:

    ne – not equal to
    lt – less than
    lte – less than or equal to
    gt – greater than
    gte – greater than or equal to
    not – negate a standard check, may be used before other operators
          (e.g. Q(age__not__mod=5))
    in – value is in list (a list of values should be provided)
    nin – value is not in list (a list of values should be provided)
    size – the size of the array, dict, or string is
    exists – value for field exists

    iexact – string field exactly matches value (case insensitive)
    contains – string field contains value
    icontains – string field contains value (case insensitive)
    startswith – string field starts with value
    istartswith – string field starts with value (case insensitive)
    endswith – string field ends with value
    iendswith – string field ends with value (case insensitive)

    isinstance - same as isinstance(field, value)
    issubclass - same as issubclass(field, value)
    """
    OPERATIONS = {
        'ne': operator.ne,
        'lt': operator.lt,
        'lte': operator.le,
        'gt': operator.gt,
        'gte': operator.ge,
        'in': lambda e, c: e in c,
        'nin': lambda e, c: e not in c,
        'size': lambda c, e: len(c) == e,
        'exists': lambda e, _: e is not None,
        'iexact': lambda s, e: s.lower() == e.lower(),
        'contains': lambda s, e: e in s,
        'icontains': lambda s, e: e.lower() in s.lower(),
        'startswith': lambda s, e: s.startswith(e),
        'istartswith': lambda s, e: s.lower().startswith(e.lower()),
        'endswith': lambda s, e: s.endswith(e),
        'iendswith': lambda s, e: s.lower().endswith(e.lower()),
        'isinstance': lambda v, c: isinstance(v, c),
        'issubclass': lambda v, c: issubclass(v, c),
    }

    @classmethod
    def and_(cls, obj, **kwargs):
        """Query an object

        :param obj:
          object to test

        :param kwargs: query specified in kwargssql

        :return:
          `True` if all `kwargs` expression are `True`, `False` otherwise.
        :rtype: bool
        """
        return cls.__eval_seqexp(obj, operator.and_, **kwargs)

    @classmethod
    def or_(cls, obj, **kwargs):
        """Query an object

        :param obj:
          object to test

        :param kwargs: query specified in kwargssql

        :return:
          `True` if at leat one `kwargs` expression is `True`,
          `False` otherwise.
        :rtype: bool
        """
        return cls.__eval_seqexp(obj, operator.or_, **kwargs)

    @classmethod
    def xor(cls, obj, **kwargs):
        """Query an object.

        :param obj:
          object to test

        :param kwargs: query specified in kwargssql

        :return:
          `True` if exactly one `kwargs` expression is `True`,
          `False` otherwise.
        :rtype: bool
        """
        return cls.__eval_seqexp(obj, operator.xor, **kwargs)

    @classmethod
    def get(cls, obj, expr):
        """Parse a kwargsql string expression, and return
        the target value in given object.

        Not sure if really needed, except when using kwargsql
        expressions in YAML files for instance.

        :param obj:
          navigation starting point

        :param basestring expr:
          kwargsql expression.

        :return:
          object pointed out by the expression.
        """
        return cls.__resolve_path(obj, expr.split('__'))

    @classmethod
    def _get_operation(cls, opname):
        """Get operation from its name.
        You can override this class method to provide additional
        operations.

        :param basestring opname:
          operation name

        :return:
          binary operator if found, `None` otherwise
        :rtype: callable object
        """
        return cls.OPERATIONS.get(opname)

    @classmethod
    def __resolve_path(cls, obj, path):
        path = filter(lambda s: s, path)
        if any(path):
            for attr in path:
                obj = cls._get_obj_attr(obj, attr)
        else:
            raise Exception("Nothing to do")
        return obj

    @classmethod
    def __eval_seqexp(cls, obj, op, **kwargs):
        return reduce(
            op,
            [cls._eval_exp(obj, exp, value)
             for (exp, value) in kwargs.items()]
        )

    @classmethod
    def _get_obj_attr(cls, obj, field):
        if isinstance(obj, dict):
            return obj.get(field)
        elif isinstance(obj, list):
            return obj[int(field)]
        else:
            return getattr(obj, field, None)

    @classmethod
    def _not(cls, op):
        def wrap(*args, **kwargs):
            return not(op(*args, **kwargs))
        return wrap

    @classmethod
    def _eval_exp(cls, obj, exp, value):
        op = operator.eq
        tokens = exp.split('__')[::-1]
        _op = cls._get_operation(tokens[0])
        if _op is not None:
            # this is the operator
            op = _op
            tokens = tokens[1:]
        if tokens[0] == 'not':
            op = cls._not(op)
            tokens = tokens[1:]
        return op(cls.__resolve_path(obj, reversed(tokens)), value)
