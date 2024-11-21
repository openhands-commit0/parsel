import re
from typing import Any, Iterable, Iterator, List, Match, Pattern, Union, cast
from w3lib.html import replace_entities as w3lib_replace_entities

def flatten(x: Iterable[Any]) -> List[Any]:
    """flatten(sequence) -> list
    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    >>> flatten(["foo", "bar"])
    ['foo', 'bar']
    >>> flatten(["foo", ["baz", 42], "bar"])
    ['foo', 'baz', 42, 'bar']
    """
    return list(iflatten(x))

def iflatten(x: Iterable[Any]) -> Iterator[Any]:
    """iflatten(sequence) -> Iterator
    Similar to ``.flatten()``, but returns iterator instead"""
    for el in x:
        if _is_listlike(el):
            yield from iflatten(el)
        else:
            yield el

def _is_listlike(x: Any) -> bool:
    """
    >>> _is_listlike("foo")
    False
    >>> _is_listlike(5)
    False
    >>> _is_listlike(b"foo")
    False
    >>> _is_listlike([b"foo"])
    True
    >>> _is_listlike((b"foo",))
    True
    >>> _is_listlike({})
    True
    >>> _is_listlike(set())
    True
    >>> _is_listlike((x for x in range(3)))
    True
    >>> _is_listlike(range(5))
    True
    """
    return hasattr(x, '__iter__') and not isinstance(x, (str, bytes))

def extract_regex(regex: Union[str, Pattern[str]], text: str, replace_entities: bool=True) -> List[str]:
    """Extract a list of strings from the given text/encoding using the following policies:
    * if the regex contains a named group called "extract" that will be returned
    * if the regex contains multiple numbered groups, all those will be returned (flattened)
    * if the regex doesn't contain any group the entire regex matching is returned
    """
    if not text:
        return []
    if replace_entities:
        text = w3lib_replace_entities(text, keep_entities=True)
    if isinstance(regex, str):
        regex = re.compile(regex)
    ret: List[str] = []
    for match in regex.finditer(text):
        if 'extract' in match.groupdict():
            ret.append(cast(str, match.group('extract')))
        elif len(match.groups()) > 0:
            ret.extend(filter(None, match.groups()))
        else:
            ret.append(match.group())
    return ret

def shorten(text: str, width: int, suffix: str='...') -> str:
    """Truncate the given text to fit in the given width."""
    if width <= 0:
        raise ValueError('Width must be greater than 0')
    if len(text) <= width:
        return text
    if width <= len(suffix):
        return text[:width]
    if width == 1:
        return '.'
    if width == 2:
        return '..'
    if width == 3:
        return '...'
    return text[:width - len(suffix)] + suffix