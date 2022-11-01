import re
from .. import Error

def temp_format(o, t: str, **kwargs):
    res = t
    # check
    obj_list = re.findall(r'[a-z]+?(?=\[)', t)
    if sum([not hasattr(o, i) for i in obj_list]) > 0:
        raise Error.FormatError(200002, [i for i in obj_list if not hasattr(o, i)])
    for i in t.split():
        k = re.search(r'[a-z]+?\b', i).group(0)
        if '*' in i:
            v = kwargs.get(k)
            join_str = i[i.index(':') + 1] if ':' in i else ','
            res = res.replace(i[i.find(k): i.index(':') + 2], join_str.join(v))
        else:
            v = getattr(o, k)
            if '[]' in i:
                res = res.replace(i, v)
            else:
                ki = re.search(r'\d+', i).group(0)
                res = res.replace(i, v[int(ki)])
    return res

def filter_format(func, check: str, **kwargs) -> str:
    # template 't'
    # 变量对照检查
    t = '{_logic} {_not} {_t_as:.}`{field}` {symbl} {value}'
    print(t)
    return 

"""
基本 模型

DB 数据库管理

Sql 基本 sql 方法对象

Tab 表模型
针对表模型进行
增 删 改 查 扩展表模型 属性

"""

class DB:
    """DB 数据库对象
    """

    def __init__(self):
        self.db_type = None
        self.db_info = None
        self.__db = None

    def set_conf(self):
        raise NotImplementedError

    def get_conf(self):
        return self.db_info

    def connect(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class Sql:
    """Sql 数据类型
    """

    def __init__(self):
        # type: query/affairs
        self.__type = None
        self.__value = None

    def get_sql(self):
        return self.__value
    
    def set_sql(self, v):
        self.__value = v
    
    def get_type(self):
        return self.__type
    
    def set_type(self, t):
        self.__type = t


class Tab:

    def __init__(self):
        self.table = None

    def set_where(self):
        # check 当对象没有该属性无法使用方法
        if not hasattr(self, 'where'):
            raise Error.UseError(200001)
    
    def get_where(self):
        # check 当对象没有该属性无法获取
        if not hasattr(self, 'where'):
            raise Error.UseError(200002)

class Insert(Tab):

    def __init__(self):
        Tab.__init__(self)
        # 字段列表
        self.fields = []
        # 数据集
        self.data = None

class Delete(Tab):

    def __init__(self):
        Tab.__init__(self)
        self.where = None
    
    def get_where(self):
        Tab.get_where(self)
        return self.where

class Update(Tab):

    def __init__(self):
        Tab.__init__(self)
        self.where = None
    
    def get_where(self):
        Tab.get_where(self)
        return self.where

class Select(Tab):

    def __init__(self):
        Tab.__init__(self)
        self.fields = []
        self.join = None
        self.where = None
        self.group = None
        self.order = None
        self.limit = None
