from functools import lru_cache
from typing import TYPE_CHECKING, Any, Optional, Protocol
from cssselect import GenericTranslator as OriginalGenericTranslator
from cssselect import HTMLTranslator as OriginalHTMLTranslator
from cssselect.parser import Element, FunctionalPseudoElement, PseudoElement
from cssselect.xpath import ExpressionError
from cssselect.xpath import XPathExpr as OriginalXPathExpr
if TYPE_CHECKING:
    from typing_extensions import Self

class XPathExpr(OriginalXPathExpr):
    textnode: bool = False
    attribute: Optional[str] = None

    def __str__(self) -> str:
        path = super().__str__()
        if self.textnode:
            if path == '*':
                path = 'text()'
            elif path.endswith('::*/*'):
                path = path[:-3] + 'text()'
            else:
                path += '/text()'
        if self.attribute is not None:
            if path.endswith('::*/*'):
                path = path[:-2]
            path += f'/@{self.attribute}'
        return path

class TranslatorProtocol(Protocol):
    def css_to_xpath(self, css: str) -> str:
        ...

class TranslatorMixin:
    """This mixin adds support to CSS pseudo elements via dynamic dispatch.

    Currently supported pseudo-elements are ``::text`` and ``::attr(ATTR_NAME)``.
    """

    def xpath_pseudo_element(self, xpath: OriginalXPathExpr, pseudo_element: PseudoElement) -> OriginalXPathExpr:
        """
        Dispatch method that transforms XPath to support pseudo-element
        """
        if isinstance(pseudo_element, FunctionalPseudoElement):
            method = f'xpath_{pseudo_element.name}_functional_pseudo_element'
            if not hasattr(self, method):
                raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}()')
            method = getattr(self, method)
            return method(xpath, pseudo_element)
        method = f'xpath_{pseudo_element.name}_simple_pseudo_element'
        if not hasattr(self, method):
            raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}')
        method = getattr(self, method)
        return method(xpath)

    def xpath_attr_functional_pseudo_element(self, xpath: OriginalXPathExpr, function: FunctionalPseudoElement) -> XPathExpr:
        """Support selecting attribute values using ::attr() pseudo-element"""
        if not function.arguments:
            raise ExpressionError("Expected at least 1 argument for ::attr(), got 0")
        if not isinstance(function.arguments[0], str):
            raise ExpressionError("Expected a string value for ::attr(), got %r" % function.arguments[0])
        xpath = XPathExpr.from_xpath(xpath)
        xpath.attribute = function.arguments[0]
        xpath.textnode = False
        return xpath

    def xpath_text_simple_pseudo_element(self, xpath: OriginalXPathExpr) -> XPathExpr:
        """Support selecting text nodes using ::text pseudo-element"""
        xpath = XPathExpr.from_xpath(xpath)
        xpath.textnode = True
        return xpath

class GenericTranslator(TranslatorMixin, OriginalGenericTranslator):
    def xpath_pseudo_element(self, xpath: OriginalXPathExpr, pseudo_element: PseudoElement) -> OriginalXPathExpr:
        if isinstance(pseudo_element, FunctionalPseudoElement):
            method = f'xpath_{pseudo_element.name}_functional_pseudo_element'
            if not hasattr(self, method):
                raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}()')
            method = getattr(self, method)
            return method(xpath, pseudo_element)
        method = f'xpath_{pseudo_element.name}_simple_pseudo_element'
        if not hasattr(self, method):
            raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}')
        method = getattr(self, method)
        return method(xpath)

class HTMLTranslator(TranslatorMixin, OriginalHTMLTranslator):
    def xpath_pseudo_element(self, xpath: OriginalXPathExpr, pseudo_element: PseudoElement) -> OriginalXPathExpr:
        if isinstance(pseudo_element, FunctionalPseudoElement):
            method = f'xpath_{pseudo_element.name}_functional_pseudo_element'
            if not hasattr(self, method):
                raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}()')
            method = getattr(self, method)
            return method(xpath, pseudo_element)
        method = f'xpath_{pseudo_element.name}_simple_pseudo_element'
        if not hasattr(self, method):
            raise ExpressionError(f'Unknown pseudo-element ::{pseudo_element.name}')
        method = getattr(self, method)
        return method(xpath)
_translator = HTMLTranslator()

@lru_cache(maxsize=5000)
def css2xpath(query: str) -> str:
    """Return translated XPath version of a given CSS query"""
    return _translator.css_to_xpath(query)