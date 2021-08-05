import collections

from django.utils.text import camel_case_to_spaces, capfirst

__all__ = ['captitle', 'deepmerge']


def captitle(title):
    return capfirst(camel_case_to_spaces(title))


def deepmerge(*dicts):
    merged = {}
    for dct in dicts:
        for key, value in dct.items():
            if not isinstance(value, dict):
                merged[key] = value
            else:
                origin = merged.get(key, {})
                merged[key] = deepmerge(origin, value)
    return merged


def indexonly(obj):
    # Checks if given object is a sequence but not a namedtuple
    # If your custom class instance passed this, then why did you do that?
    return (isinstance(obj, collections.Sequence) and not
            hasattr(obj, '_make') and not hasattr(obj, '_replace'))
