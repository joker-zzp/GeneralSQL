from .. import Error
from .base import DB, Sql
from .base import (
    Insert as JI,
    Delete as JD,
    Update as JU,
    Select as JS,
)

class TDB(DB):...

class TInsert(JI, Sql):

    def __init__(self, table, data:list|dict):
        JI.__init__(self)
        Sql.__init__(self)
        self.set_type('affairs')
        self.table = table
        self.data = data

    def data_decode(self): raise NotImplementedError
    
    def format_sql(self): raise NotImplementedError

class TUpdate(JU, Sql):

    def __init__(self, table, data:dict):
        JU.__init__(self)
        Sql.__init__(self)
        self.set_type('affairs')
        self.table = table
        self.data = data

    def data_decode(self): raise NotImplementedError

    def format_sql(self): raise NotImplementedError

class TDelete(JD, Sql):

    def __init__(self, table):
        JD.__init__(self)
        Sql.__init__(self)
        self.set_type('affairs')
        self.table = table

    def format_sql(self): raise NotImplementedError

class TSelect(JS, Sql):

    def __init__(self, /, **kwargs):
        JS.__init__(self)
        Sql.__init__(self)
        self.set_type('query')
        if kwargs.get('table'):
            self.table = kwargs.get('table')

    def format_sql(self): raise NotImplementedError

    def format_data(self): raise NotImplementedError

__all__ = [
    'TDB',
    'TInsert',
    'TUpdate',
    'TDelete',
    'TSelect',
]
