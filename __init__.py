import importlib
import functools
from . import db

__version__ = '1.1.6'

__cls__ = db.__all__


def SeniorDB(t):
    if t in __cls__:
        __db = getattr(db, t).DB
    else:
        __db = importlib.import_module(name = t).DB
    
    class SeniorDB(__db):...
    return SeniorDB()


def SeniorSQL(o: SeniorDB):
    t = o.db_type
    if t in __cls__:
        pack = getattr(db, t)
    else:
        pack = importlib.import_module(name = t)

    class SeniorSQL(*[getattr(pack, i) for i in pack.__all__]):
        
        def __init__(self):...

        def Add(self, *args, **kwargs):
            pack.Insert.__init__(self, *args, **kwargs)
            self.func = 'Insert'

        def Del(self, *args, **kwargs):
            pack.Delete.__init__(self, *args, **kwargs)
            self.func = 'Delete'

        def Up(self, *args, **kwargs):
            pack.Update.__init__(self, *args, **kwargs)
            self.func = 'Update'
        
        def Sel(self, *args, **kwargs):
            pack.Select.__init__(self, *args, **kwargs)
            self.func = 'Select'

        def __run_class_func(func):
            @functools.wraps(func)
            def f(self, *args, **kwargs):
                return getattr(getattr(pack, self.func), func.__name__)(self, *args, **kwargs)
            return f
        
        @__run_class_func
        def set_join(self, *args, **kwargs):...

        @__run_class_func
        def set_where(self, *args, **kwargs):...

        @__run_class_func
        def set_group(self, *args, **kwargs):...
        
        @__run_class_func
        def set_order(self, *args, **kwargs):...

        @__run_class_func
        def set_limit(self, *args, **kwargs):...

        @__run_class_func
        def data_decode(self, *args, **kwargs):...

        @__run_class_func
        def format_sql(self, *args, **kwargs):
            """格式化 SQL 语句
            """
            pass

        @__run_class_func
        def format_data(self, *args, **kwargs) -> list|dict:
            """格式化数据

            Returns:
                list|dict: 结果
            """
            pass

    return SeniorSQL()
