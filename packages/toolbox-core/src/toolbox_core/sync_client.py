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
from threading import Thread
from typing import Any, Awaitable, Callable, Mapping, Optional, TypeVar, Union

from aiohttp import ClientSession

from .client import ToolboxClient
from .sync_tool import ToolboxSyncTool

T = TypeVar("T")


class ToolboxSyncClient:
    """
    A synchronous client for interacting with a Toolbox service.

    Provides methods to discover and load tools defined by a remote Toolbox
    service endpoint, returning synchronous tool wrappers (`ToolboxSyncTool`).
    It manages an underlying asynchronous `ToolboxClient`.
    """

    __session: Optional[ClientSession] = None
    __loop: Optional[asyncio.AbstractEventLoop] = None
    __thread: Optional[Thread] = None

    def __init__(
        self,
        url: str,
    ):
        """
        Initializes the ToolboxSyncClient.

        Args:
            url: The base URL for the Toolbox service API (e.g., "http://localhost:5000").
        """
        # Running a loop in a background thread allows us to support async
        # methods from non-async environments.
        if ToolboxSyncClient.__loop is None:
            loop = asyncio.new_event_loop()
            thread = Thread(target=loop.run_forever, daemon=True)
            thread.start()
            ToolboxSyncClient.__thread = thread
            ToolboxSyncClient.__loop = loop

        async def __start_session() -> None:
            # Use a default session if none is provided. This leverages connection
            # pooling for better performance by reusing a single session throughout
            # the application's lifetime.
            if ToolboxSyncClient.__session is None:
                ToolboxSyncClient.__session = ClientSession()

        coro = __start_session()

        asyncio.run_coroutine_threadsafe(__start_session(), ToolboxSyncClient.__loop).result()

        if not ToolboxSyncClient.__session:
            raise ValueError("Session cannot be None.")
        self.__async_client = ToolboxClient(url, ToolboxSyncClient.__session)

    def __run_as_sync(self, coro: Awaitable[T]) -> T:
        """Run an async coroutine synchronously"""
        if not self.__loop:
            raise Exception(
                "Cannot call synchronous methods before the background loop is initialized."
            )
        return asyncio.run_coroutine_threadsafe(coro, self.__loop).result()

    async def __run_as_async(self, coro: Awaitable[T]) -> T:
        """Run an async coroutine asynchronously"""

        # If a loop has not been provided, attempt to run in current thread.
        if not self.__loop:
            return await coro

        # Otherwise, run in the background thread.
        return await asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(coro, self.__loop)
        )

    def load_tool(
        self,
        tool_name: str,
        auth_token_getters: dict[str, Callable[[], str]] = {},
        bound_params: Mapping[str, Union[Callable[[], Any], Any]] = {},
    ) -> ToolboxSyncTool:
        """
        Synchronously loads a tool from the server.

        Retrieves the schema for the specified tool and returns a callable,
        synchronous object (`ToolboxSyncTool`) that can be used to invoke the
        tool remotely.

        Args:
            tool_name: Name of the tool to load.
            auth_token_getters: A mapping of authentication service names to
                callables that return the corresponding authentication token.
            bound_params: A mapping of parameter names to bind to specific values or
                callables that are called to produce values as needed.

        Returns:
            ToolboxSyncTool: A synchronous callable object representing the loaded tool.
        """

        async_tool = self.__run_as_sync(
            self.__async_client.load_tool(tool_name, auth_token_getters, bound_params)
        )

        if not self.__loop or not self.__thread:
            raise ValueError("Background loop or thread cannot be None.")
        return ToolboxSyncTool(async_tool, self.__loop, self.__thread)

    def load_toolset(
        self,
        toolset_name: str,
        auth_token_getters: dict[str, Callable[[], str]] = {},
        bound_params: Mapping[str, Union[Callable[[], Any], Any]] = {},
    ) -> list[ToolboxSyncTool]:
        """
        Synchronously fetches a toolset and loads all tools defined within it.

        Args:
            toolset_name: Name of the toolset to load tools from.
            auth_token_getters: A mapping of authentication service names to
                callables that return the corresponding authentication token.
            bound_params: A mapping of parameter names to bind to specific values or
                callables that are called to produce values as needed.

        Returns:
            list[ToolboxSyncTool]: A list of synchronous callables, one for each
            tool defined in the toolset.
        """

        async_tools = self.__run_as_sync(
            self.__async_client.load_toolset(
                toolset_name, auth_token_getters, bound_params
            )
        )

        if not self.__loop or not self.__thread:
            raise ValueError("Background loop or thread cannot be None.")
        tools: list[ToolboxSyncTool] = []
        for async_tool in async_tools:
            tools.append(ToolboxSyncTool(async_tool, self.__loop, self.__thread))
        return tools

    def close(self):
        """
        Synchronously closes the client session if it was created internally by the client.
        """
        coro = self.__session.close()
        self.__run_as_sync(coro)

    def __enter__(self):
        """Enter the runtime context related to this client instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the client session."""
        self.close()
