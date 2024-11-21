import re
from typing import Any, Callable, Optional
from lxml import etree
from w3lib.html import HTML5_WHITESPACE
regex = f'[{HTML5_WHITESPACE}]+'
replace_html5_whitespaces = re.compile(regex).sub

def setup() -> None:
    """Register built-in XPath extension functions."""
    set_xpathfunc("has-class", has_class)

def set_xpathfunc(fname: str, func: Optional[Callable]) -> None:
    """Register a custom extension function to use in XPath expressions.

    The function ``func`` registered under ``fname`` identifier will be called
    for every matching node, being passed a ``context`` parameter as well as
    any parameters passed from the corresponding XPath expression.

    If ``func`` is ``None``, the extension function will be removed.

    See more `in lxml documentation`_.

    .. _`in lxml documentation`: https://lxml.de/extensions.html#xpath-extension-functions

    """
    ns = etree.FunctionNamespace(None)
    if func is None:
        del ns[fname]
    else:
        ns[fname] = func

def has_class(context: Any, *classes: str) -> bool:
    """has-class function.

    Return True if all ``classes`` are present in element's class attr.

    """
    if not classes:
        raise ValueError("has-class must have at least 1 argument")

    for class_ in classes:
        if not isinstance(class_, str):
            raise ValueError("has-class arguments must be strings")
        try:
            class_.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError("All strings must be XML compatible")

    element = context.context_node
    class_attr = element.get('class', '').strip()
    if not class_attr:
        return False

    element_classes = set(replace_html5_whitespaces(' ', class_attr).split())
    return all(class_ in element_classes for class_ in classes)