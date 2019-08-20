# coding: utf-8
# © 2016-2019 Resurface Labs Inc.
from typing import Dict, List, ItemsView, Optional, Set, Tuple, Union
from urllib.parse import parse_qsl, urlsplit, SplitResult


class HttpRequestImpl(object):
    """
    HTTP Request Object

    :param method (Optional): HTTP request method; see valid methods below
    :param request_url (Optional): Full request URL including query string
    :param headers (Optional): HTTP request headers
    :param body (Optional): HTTP request body
    :return: :class: HttpRequestImpl object
    """

    VALID_REQUEST_METHODS: Set[str] = {'GET', 'HEAD', 'POST', 'PUT', 'DELETE',
                                       'PATCH', 'TRACE', 'OPTIONS', 'CONNECT'}
    VALID_SCHEMES: Dict[str, int] = {'https': 443, 'http': 80}

    def __init__(self, method: Optional[str] = None,
                 request_url: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 body: Optional[Union[bytes, str]] = None) -> None:

        self._scheme: Optional[str] = None
        self._port: Optional[int] = None

        self.host: str = ''
        self.path: str = ''
        self.query_string: str = ''

        self.method = method
        self.request_url = request_url
        self.headers = {} if headers is None else headers
        self.body = body

    # self.method getter/setter
    @property
    def method(self) -> Optional[str]:
        return self._method

    @method.setter
    def method(self, value: Optional[str]) -> None:
        if value is None or value in self.VALID_REQUEST_METHODS:
            self._method = value
        else:
            raise TypeError('incorrect HTTP method')

    # self.request_url getter/setter
    @property
    def request_url(self) -> Optional[str]:
        """Rebuilds and returns the full URL using base_url, full_path"""
        url_builder = ''
        if self.base_url:
            url_builder = url_builder + self.base_url
            if self.full_path:
                url_builder = url_builder + self.full_path
        return url_builder

    @request_url.setter
    def request_url(self, value: str) -> None:
        """Splits given URL and updates base_url, path, query_string"""
        if value:
            u: SplitResult = urlsplit(value)
            self.base_url = '{0}://{1}'.format(u.scheme, u.netloc)
            self.path = u.path
            self.query_string = u.query

    # self.body getter/setter
    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: Optional[Union[bytes, str]]):
        if isinstance(value, str):
            self._body = bytes(value, 'utf8')
        elif isinstance(value, bytes):
            self._body = value

    # self.base_url getter/setter
    @property
    def base_url(self) -> str:
        """Rebuilds and returns the base URL using scheme, host, port"""
        url_builder = ''
        if self._scheme and self.host:
            url_builder = "{0}://{1}".format(self._scheme, self.host)
            if self._port and self._port not in {80, 443}:
                url_builder = url_builder + ":{0}".format(str(self._port))
        return url_builder

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Splits URL and updates scheme, host, port"""
        u: SplitResult = urlsplit(value)
        if u.netloc:
            self.scheme = u.scheme
            self.host = u.hostname
            self.port = self._port_matcher(u.port, u.scheme)
        else:
            raise TypeError('invalid base URL')

    # self.scheme getter/setter
    @property
    def scheme(self) -> Optional[str]:
        return self._scheme

    @scheme.setter
    def scheme(self, value: str) -> None:
        """Verifies scheme is valid and updates scheme, port (when needed)"""
        if value in self.VALID_SCHEMES:
            self._scheme = value
            # Update port if we are using a common port
            if self._port in self.VALID_SCHEMES.values():
                self._port = self._port_matcher(None, self._scheme)
        else:
            raise TypeError('incorrect URL scheme')

    # self.port getter/setter
    @property
    def port(self) -> Optional[int]:
        return self._port

    @port.setter
    def port(self, value: int) -> None:
        """Updates port, scheme (when needed)"""
        if isinstance(value, int):
            self._port = value
            # Update scheme in case we switched to a common port
            if self._port in self.VALID_SCHEMES.values():
                self._scheme = self._scheme_matcher(self._port)
        else:
            raise TypeError('invalid HTTP port')

    # self.full_path getter
    @property
    def full_path(self) -> Optional[str]:
        """Rebuilds and returns the full path using path, query_string"""
        path_builder = ''
        if self.path:
            path_builder = path_builder + self.path
        # Unlike URL methods, process query string even if path is blank
        if self.query_string:
            path_builder = "{0}?{1}".format(path_builder, self.query_string)
        return path_builder

    # formatters
    def get_headers(self) -> ItemsView[str, str]:
        return self.headers.items()

    def get_query_params(self) -> List[Tuple[str, str]]:
        return parse_qsl(self.query_string, keep_blank_values=True)

    # Private
    def _scheme_matcher(self, port: Union[int, str]):
        return next((
            s for s, p in self.VALID_SCHEMES.items() if p == int(port)), None)

    def _port_matcher(self, port: Optional[Union[int, str]],
                      scheme: str) -> Optional[int]:
        if port is None:
            return next((
                p for s, p in self.VALID_SCHEMES.items() if s == scheme), None)
        else:
            return int(port)
