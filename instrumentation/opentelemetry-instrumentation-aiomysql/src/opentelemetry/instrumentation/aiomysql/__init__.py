# Copyright The OpenTelemetry Authors
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

"""
The integration with MySQL supports the aiomysql library,
it can be enabled by using ``AiomysqlInstrumentor``.

.. aiomysql: https://github.com/aio-libs/aiomysql

Usage
-----

.. code-block:: python

    import asyncio
    import aiomysql
    from opentelemetry.instrumentation.aiomysql import AiomysqlInstrumentor
    # Call instrument() to wrap all database connections
    AiomysqlInstrumentor().instrument()

    dsn = 'user=user password=password host=127.0.0.1'

    async def connect():
        cnx = await aiomysql.connect(dsn)
        cursor = await cnx.cursor()
        await cursor.execute("CREATE TABLE IF NOT EXISTS test (testField INTEGER)")
        await cursor.execute("INSERT INTO test (testField) VALUES (123)")
        cursor.close()
        cnx.close()

    async def create_pool():
        pool = await aiomysql.create_pool(dsn)
        cnx = await pool.acquire()
        cursor = await cnx.cursor()
        await cursor.execute("CREATE TABLE IF NOT EXISTS test (testField INTEGER)")
        await cursor.execute("INSERT INTO test (testField) VALUES (123)")
        cursor.close()
        cnx.close()

    asyncio.run(connect())
    asyncio.run(create_pool())

.. code-block:: python

    import asyncio
    import aiomysql
    from opentelemetry.instrumentation.aiomysql import AiomysqlInstrumentor

    dsn = 'user=user password=password host=127.0.0.1'

    # Alternatively, use instrument_connection for an individual connection
    async def go():
        cnx = await aiomysql.connect(dsn)
        instrumented_cnx = AiomysqlInstrumentor().instrument_connection(cnx)
        cursor = await instrumented_cnx.cursor()
        await cursor.execute("CREATE TABLE IF NOT EXISTS test (testField INTEGER)")
        await cursor.execute("INSERT INTO test (testField) VALUES (123)")
        cursor.close()
        instrumented_cnx.close()

    asyncio.run(go())

API
---
"""

from typing import Collection

from opentelemetry.instrumentation.aiomysql import wrappers
from opentelemetry.instrumentation.aiomysql.package import _instruments
from opentelemetry.instrumentation.aiomysql.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor


class AiomysqlInstrumentor(BaseInstrumentor):
    _CONNECTION_ATTRIBUTES = {
        "database": "db",
        "port": "port",
        "host": "host",
        "user": "user",
    }

    _DATABASE_SYSTEM = "mysql"

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Integrate with MySQL aiomysql library.
        aiomysql: https://github.com/aio-libs/aiomysql
        """

        tracer_provider = kwargs.get("tracer_provider")

        wrappers.wrap_connect(
            __name__,
            self._DATABASE_SYSTEM,
            self._CONNECTION_ATTRIBUTES,
            version=__version__,
            tracer_provider=tracer_provider,
        )

        wrappers.wrap_create_pool(
            __name__,
            self._DATABASE_SYSTEM,
            self._CONNECTION_ATTRIBUTES,
            version=__version__,
            tracer_provider=tracer_provider,
        )

    # pylint:disable=no-self-use
    def _uninstrument(self, **kwargs):
        """ "Disable aiomysql instrumentation"""
        wrappers.unwrap_connect()
        wrappers.unwrap_create_pool()

    # pylint:disable=no-self-use
    def instrument_connection(self, connection, tracer_provider=None):
        """Enable instrumentation in a aiomysql connection.

        Args:
            connection: The connection to instrument.
            tracer_provider: The optional tracer provider to use. If omitted
                the current globally configured one is used.

        Returns:
            An instrumented connection.
        """
        return wrappers.instrument_connection(
            __name__,
            connection,
            self._DATABASE_SYSTEM,
            self._CONNECTION_ATTRIBUTES,
            version=__version__,
            tracer_provider=tracer_provider,
        )

    def uninstrument_connection(self, connection):
        """Disable instrumentation in a aiomysql connection.

        Args:
            connection: The connection to uninstrument.

        Returns:
            An uninstrumented connection.
        """
        return wrappers.uninstrument_connection(connection)
