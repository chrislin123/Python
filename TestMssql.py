
from collections import deque

import pymssql

import pydapper

import datetime
from dataclasses import dataclass

from pydapper import connect


class SimplePool:
    """pymssql does not provide a pool interface, this is a simple example that should never be used in production"""

    def __init__(self, **connect_kwargs):
        self._connect_kwargs = connect_kwargs
        self._connections = deque()

    def getconn(self):
        if len(self._connections) == 0:
            return pymssql.connect(**self._connect_kwargs)
        return self._connections.pop()

    def putconn(self, conn):
        self._connections.append(conn)

    def __del__(self):
        for conn in self._connections:
            conn.close()


my_pool = SimplePool(server="10.8.0.6", port=1433, user="sa", password="pass@word1", database="C10")

commands = pydapper.using(my_pool.getconn())
print(type(commands))
# <class 'pydapper.mssql.pymssql.PymssqlCommands'>

print(type(commands.connection))
# <class 'pymssql._pymssql.Connection'>

my_pool.putconn(commands.connection)

#StockInfo


@dataclass
class Task:
    stockcode: str
    stockname: str
    # due_date: datetime.date
    # owner_id: int

query = """
  select stockcode,stockname  from StockInfo
"""

# with connect() as commands:
data = commands.query(query, model=Task)


print(data)
