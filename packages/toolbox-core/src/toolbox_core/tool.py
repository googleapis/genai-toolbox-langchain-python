# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio
import types
from collections import defaultdict
from inspect import Parameter, Signature
from typing import (
    Any,
    Callable,
    DefaultDict,
    TypeVar,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Union,
)

from aiohttp import ClientSession
from pytest import Session

T = TypeVar('T')


class ToolboxTool:
    """
    A callable proxy object representing a specific tool on a remote Toolbox server.

    Instances of this class behave like asynchronous functions. When called, they
    send a request to the corresponding tool's endpoint on the Toolbox server with
    the provided arguments.

    It utilizes Python's introspection features (`__name__`, `__doc__`,
    `__signature__`, `__annotations__`) so that standard tools like `help()`
    and `inspect` work as expected.
    """

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        name: str,
        desc: str,
        params: Sequence[Parameter],
        required_authn_params: Mapping[str, list[str]],
        auth_service_token_getters: Mapping[str, Callable[[], str]],
        bound_params: Mapping[str, Union[Callable[[], Any], Any]] = {},
    ):
        """
        Initializes a callable that will trigger the tool invocation through the
        Toolbox server.

        Args:
            session: The `aiohttp.ClientSession` used for making API requests.
            base_url: The base URL of the Toolbox server API.
            name: The name of the remote tool.
            desc: The description of the remote tool (used as its docstring).
            params: A list of `inspect.Parameter` objects defining the tool's
                arguments and their types/defaults.
            required_authn_params: A dict of required authenticated parameters that
                need a auth_service_token_getter set for them yet.
            auth_service_tokens: A dict of authService -> token (or callables that
                produce a token)
        """

        # used to invoke the toolbox API
        self.__session: ClientSession = session
        self.__base_url: str = base_url
        self.__url = f"{base_url}/api/tool/{name}/invoke"

        self.__desc = desc
        self.__params = params

        # the following properties are set to help anyone that might inspect it determine usage
        self.__name__ = name
        self.__doc__ = desc
        self.__signature__ = Signature(parameters=params, return_annotation=str)
        self.__annotations__ = {p.name: p.annotation for p in params}
        # TODO: self.__qualname__ ??

        # map of parameter name to auth service required by it
        self.__required_authn_params = required_authn_params
        # map of authService -> token_getter
        self.__auth_service_token_getters = auth_service_token_getters
        # map of parameter name to value or Callable
        self.__bound_parameters = bound_params

    def __copy(
        self,
        session: Optional[ClientSession] = None,
        base_url: Optional[str] = None,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        params: Optional[list[Parameter]] = None,
        required_authn_params: Optional[Mapping[str, list[str]]] = None,
        auth_service_token_getters: Optional[Mapping[str, Callable[[], str]]] = None,
        bound_params: Optional[Mapping[str, Union[Callable[[], Any], Any]]] = None,
    ) -> "ToolboxTool":
        """
        Creates a copy of the ToolboxTool, overriding specific fields.

        Args:
            session: The `aiohttp.ClientSession` used for making API requests.
            base_url: The base URL of the Toolbox server API.
            name: The name of the remote tool.
            desc: The description of the remote tool (used as its docstring).
            params: A list of `inspect.Parameter` objects defining the tool's
                arguments and their types/defaults.
            required_authn_params: A dict of required authenticated parameters that need
                a auth_service_token_getter set for them yet.
            auth_service_token_getters: A dict of authService -> token (or callables
                that produce a token)

        """

        def _resolve_value(override_value: Optional[T], default_value: T) -> T:
            """Returns the override_value if it's not None, otherwise the default_value."""
            return override_value if override_value is not None else default_value

        return ToolboxTool(
            session=_resolve_value(session, self.__session),
            base_url=_resolve_value(base_url, self.__base_url),
            name=_resolve_value(name, self.__name__),
            desc=_resolve_value(desc, self.__desc),
            params=_resolve_value(params, self.__params),
            required_authn_params=_resolve_value(required_authn_params, self.__required_authn_params),
            auth_service_token_getters=_resolve_value(auth_service_token_getters, self.__auth_service_token_getters),
            bound_params=_resolve_value(bound_params, self.__bound_parameters),
        )

    async def __call__(self, *args: Any, **kwargs: Any) -> str:
        """
        Asynchronously calls the remote tool with the provided arguments.

        Validates arguments against the tool's signature, then sends them
        as a JSON payload in a POST request to the tool's invoke URL.

        Args:
            *args: Positional arguments for the tool.
            **kwargs: Keyword arguments for the tool.

        Returns:
            The string result returned by the remote tool execution.
        """

        # check if any auth services need to be specified yet
        if len(self.__required_authn_params) > 0:
            req_auth_services = set(l for l in self.__required_authn_params.keys())
            raise Exception(
                f"One of more of the following authn services are required to invoke this tool: {','.join(req_auth_services)}"
            )

        # validate inputs to this call using the signature
        all_args = self.__signature__.bind(*args, **kwargs)
        all_args.apply_defaults()  # Include default values if not provided
        payload = all_args.arguments

        # apply bounded parameters
        for param, value in self.__bound_parameters.items():
            if asyncio.iscoroutinefunction(value):
                value = await value()
            elif callable(value):
                value = value()
            payload[param] = value

        # create headers for auth services
        headers = {}
        for auth_service, token_getter in self.__auth_service_token_getters.items():
            headers[f"{auth_service}_token"] = token_getter()

        async with self.__session.post(
            self.__url,
            json=payload,
            headers=headers,
        ) as resp:
            body = await resp.json()
            if resp.status < 200 or resp.status >= 300:
                err = body.get("error", f"unexpected status from server: {resp.status}")
                raise Exception(err)
        return body.get("result", body)

    def add_auth_token_getters(
        self,
        auth_token_getters: Mapping[str, Callable[[], str]],
    ) -> "ToolboxTool":
        """
        Registers a auth token getter function that is used for AuthServices when tools
        are invoked.

        Args:
            auth_token_getters: A mapping of authentication service names to
                callables that return the corresponding authentication token.

        Returns:
            A new ToolboxTool instance with the specified authentication token
            getters registered.
        """

        # throw an error if the authentication source is already registered
        dupes = auth_token_getters.keys() & self.__auth_service_token_getters.keys()
        if dupes:
            raise ValueError(
                f"Authentication source(s) `{', '.join(dupes)}` already registered in tool `{self.__name__}`."
            )

        # create a read-only updated value for new_getters
        new_getters = types.MappingProxyType(
            dict(self.__auth_service_token_getters, **auth_token_getters)
        )
        # create a read-only updated for params that are still required
        new_req_authn_params = types.MappingProxyType(
            filter_required_authn_params(
                self.__required_authn_params, auth_token_getters.keys()
            )
        )

        return self.__copy(
            auth_service_token_getters=new_getters,
            required_authn_params=new_req_authn_params,
        )

    def bind_parameters(
        self, bound_params: Mapping[str, Callable[[], str]]
    ) -> "ToolboxTool":
        """
        Binds parameters to values or callables that produce values.

         Args:
             bound_params: A mapping of parameter names to values or callables that
                 produce values.

         Returns:
             A new ToolboxTool instance with the specified parameters bound.
        """
        all_params = set(p.name for p in self.__params)
        for name in bound_params.keys():
            if name not in all_params:
                raise Exception(f"unable to bind parameters: no parameter named {name}")

        new_params = []
        for p in self.__params:
            if p.name not in bound_params:
                new_params.append(p)

        return self.__copy(
            params=new_params,
            bound_params=bound_params,
        )


def filter_required_authn_params(
    req_authn_params: Mapping[str, list[str]], auth_services: Iterable[str]
) -> dict[str, list[str]]:
    """
    Utility function for reducing 'req_authn_params' to a subset of parameters that
    aren't supplied by a least one service in auth_services.

    Args:
        req_authn_params: A mapping of parameter names to sets of required
            authentication services.
        auth_services: An iterable of authentication service names for which
            token getters are available.

    Returns:
        A new dictionary representing the subset of required authentication parameters
        that are not covered by the provided `auth_services`.
    """
    req_params = {}
    for param, services in req_authn_params.items():
        # if we don't have a token_getter for any of the services required by the param, the param is still required
        required = not any(s in services for s in auth_services)
        if required:
            req_params[param] = services
    return req_params
