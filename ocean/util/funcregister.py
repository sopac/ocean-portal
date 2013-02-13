#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from functools import wraps

class Parameterise(object):
    """
    apply_to is a decorator which makes it possible to implement
    multiple versions of a method, based on the passed parameters, for instance:

    class MyClass(object):
        p = Parameterise()

        @p.apply_to(variable='anom', period='monthly')
        def get_title(self, *args, params={}):
            ...

    Would only apply in the case where params included variable and period
    with their respective values.

    The method is then called something like:
        dataset.get_title(params={...})

    If a method matches too many versions, or is otherwise ambiguous,
    AttributeError is raised. Similarly if there are no available matches.
    """

    def __init__(self):
        self._registry = {}

    def apply_to(self, **methodparams):
        """
        This is the decorator.
        """

        def outer(func):
            name = func.__name__

            try:
                funcs = self._registry[name]
            except KeyError:
                funcs = self._registry[name] = []

            funcs.append(func)
            func._methodparams = methodparams

            def matches(params, ignores):
                def inner(func):
                    for k, v in func._methodparams.items():
                        if k in ignores:
                            return False

                        if k not in params or params[k] != v:
                            return False

                    return True

                return inner

            @wraps(func)
            def inner(*args, **kwargs):
                params = kwargs['params']

                try:
                    ignore = kwargs['_ignore']
                    del kwargs['_ignore']
                except KeyError:
                    ignore = []

                candidates = filter(matches(params, ignore), funcs)
                candidates.sort(key=lambda f: len(f._methodparams),
                                reverse=True)

                if len(candidates) == 1:
                    return candidates[0](*args, **kwargs)
                elif len(candidates) > 1:
                    if len(candidates[0]._methodparams) == \
                       len(candidates[1]._methodparams):
                        for c in candidates:
                            print c._methodparams
                        raise AttributeError("Ambiguous. Too many matches")
                    else:
                        return candidates[0](*args, **kwargs)
                else:
                    raise AttributeError("No function matches parameters")

            return inner

        return outer
