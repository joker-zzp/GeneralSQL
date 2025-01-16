from ..Template import *
from .. import Error
import datetime

def _data_dict(fields: tuple, datas: list) -> list:
    res = []
    keys = range(len(fields))
    for v in datas:
        tmp = {}
        for k in keys:
            tmp.update({fields[k]: str(v[k])})
        res.append(tmp)
    return res

def _data_table(fields: tuple, datas: list) -> dict:
    res = {
        'header': list(fields),
        'data': [[d for d in i] for i in datas],
    }
    return res

def _filter_format(filter_data:dict) -> str:
    # 检查
    if not set(filter_data.keys()) >= set(['symbol', 'field', 'value']): raise Error.ParamsError(400003, 'Params miss in [symbol, field, value]')

    symbol_list = ['=', '<=', '>=', '!=', '<>', '<', '>', 'IN', 'LIKE', 'BETWEEN', 'ISNULL']
    result = ''
    # factor_list = ['AND', 'OR', 'NOT']
    # check symbol
    symbol, field, val = str(filter_data.get('symbol')).upper(), f"{filter_data.get('field')}", filter_data.get('value')

    # 条件逻辑处理
    symbol:str = filter_data.get('symbol').upper()
    if symbol == None: raise Error.ParamsError(400003, 'Params miss in [symbol, field, value]')
    if symbol not in symbol_list: raise Error.ParamsError(400004)
    symbol = symbol.upper()

    # 表 as 名称替换 field
    if filter_data.get('table_as'):
        field = f"{filter_data.get('table_as')}.`{field}`"

    # 自定义 value 处理
    if filter_data.get('val_format'):
        val = filter_data.get('val_format')(val)
    else:
        # 默认 value 处理
        if isinstance(val, (dict)) and val.get('start') and val.get('end'):
            val = f'{repr(val.get("start"))} AND {repr(val.get("end"))}'
        elif isinstance(val, (tuple, list)) and symbol == 'IN':
            val = ','.join([repr(str(i)) for i in val])
        else:
            val = repr(val)

    if symbol == 'ISNULL':
        return f'{result} {symbol}({field})'
    else:
        return f'{result} {field} {symbol} ({val})'


class SqlBase:

    def __init__(self):
        self.sql_template: str | list = None
        self.params = []

    # def get_sql(self):
    #     if self.sql_template is None:
    #         raise Error.UseError(200001)
    #     if isinstance(self.sql_template, str):
    #         # 将字符串中 ? 替换成 {}
    #         _template = self.sql_template.replace('?', '{}')
    #         return _template.format(*self.params)
    #     if isinstance(self.sql_template, list):
    #         # insert [str, str] params -> [[], []]
    #         res = []
    #         if len(self.sql_template) != len(self.params):
    #             raise Error.ParamsError(400002, 'params len != sql_template len')
    #         for i in range(len(self.sql_template)):
    #             # 将字符串中 ? 替换成 {}
    #             _template = self.sql_template[i].replace('?', '{}')
    #             res.append(_template.format(*self.params[i]))
    #         return res
    #     raise Error.ParamsError(400003, 'sql_template type error')

    # 获取原始数据
    def get_values(self) -> list | dict:
        if isinstance(self.sql_template, str):
            return {'template': self.sql_template, 'params': self.params}
        if isinstance(self.sql_template, list):
            return [{'template': it, 'params': self.params[i]} for i, it in enumerate(self.sql_template)]
        return {}

class SqlWhere:

    def __init__(self):
        self.where = None

    def set_where(self, *filters):
        self.where = []
        if len(filters) < 1: raise Error.ParamsError(400002)
        factor_list = ['AND', 'OR', 'NOT']
        filters = list(filter(lambda x: isinstance(x, dict), filters))
        if isinstance(filters[0], dict) and filters[0].get('factor'):
            filters[0].pop('factor')

        gl_index = []
        for i, v in enumerate(filters):
            if v.get('val_factor') and i > 0:
                self.where[-1] += f' {v.get("val_factor")}{_filter_format(v)}'
                continue
            gl_index.append(i)
            self.where.append(_filter_format(v))
        for i, v in enumerate(self.where):
            if gl_index[i]:
                if filters[gl_index[i]].get('factor', '').upper() in factor_list:
                    tmp_factor = str(filters[gl_index[i]].get('factor', '')).upper()
                    self.where[i] = f'{tmp_factor} ({v})'
                else:
                    raise Error.ParamsError(400003, 'factor not in ["AND", "OR", "NOT"]')
            else:
                self.where[i] = f'({v})'
        self.where = f'WHERE {" ".join(self.where)}'
        return self

class Insert(SqlBase, TInsert):

    def __init__(self, table_name, data: dict | list):
        SqlBase.__init__(self)
        TInsert.__init__(self, table_name, data)
        self.__sql_template = 'INSERT INTO {} ({}) VALUES ({})'
        # self.__base = ['INSERT INTO', 'VALUES']
        self.val_max = 5
        self.values = []
        if not isinstance(data, (dict, list)):
            Error.ParamsError(400001)

        if isinstance(data, dict):
            self.fields = list(data.keys())

        if isinstance(data, list):
            self.fields = list(set.union(*[set(i.keys()) for i in data if isinstance(i, dict)]))

    def get_sql(self):
        if self.sql_template is None:
            return TInsert.get_sql(self)
        return SqlBase.get_values(self)

    def data_decode(self, data: dict = None):
        if isinstance(self.data, dict) or data:
            _d: dict = data if data else self.data
            # 循环字段列表中数据 不存在 key
            data_list = [data.get(i) if i in data.keys() and data.get(i) != None else 'NULL' for i in self.fields]
            self.values.append(tuple(data_list))
        elif isinstance(self.data, list):
            for item in self.data:
                self.data_decode(item)
        else:
            raise Error.ParamsError(400001)

    def format_sql(self):
        if not self.values:
            self.data_decode()
        # res = []
        field = ','.join(self.fields)
        # 根据 fields 长度生成占位符
        _val_d = ','.join(['?'] * len(self.fields))
        self.sql_template = []
        # format_insert = lambda x: f"{self.__base[0]} {self.table} ({field}) {self.__base[1]} {x}"
        for i in range(0, len(self.values), self.val_max):
            # 分批插入 0:5 5:10 10:15 ...
            self.sql_template.append(self.__sql_template.format(self.table, field, _val_d))
            self.params.append(self.values[i:i + self.val_max])
        # self.set_sql(res)

class Delete(SqlBase, TDelete, SqlWhere):

    def __init__(self, table):
        SqlBase.__init__(self)
        TDelete.__init__(self, table)
        SqlWhere.__init__(self)
        self.__sql_template = 'DELETE FROM {}'

    def set_where(self, *filters):
        return SqlWhere.set_where(self, *filters)

    def format_sql(self):
        self.sql_template = self.__sql_template.format(self.table)
        if self.where:
            self.sql_template += f' {self.where}'
        # self.set_sql(sql)
        self.params = tuple(self.params)

class Update(SqlBase, TUpdate, SqlWhere):

    def __init__(self, table, data: dict):
        SqlBase.__init__(self)
        TUpdate.__init__(self, table, data)
        SqlWhere.__init__(self)
        self.__sql_template = 'UPDATE {} SET {}'

    def set_where(self, *filters):
        return SqlWhere.set_where(self, *filters)

    def data_decode(self):
        if not hasattr(self, 'data') or self.data is None:
            raise Error.UseError(200002)
        if not isinstance(self.data, dict):
            raise Error.ParamsError(400001)
        kx = []
        vx = []
        for k, v in self.data.items():
            kx.append(f'{k} = ?')
            self.params.append(v)
        self.value = {
            'key': ','.join(kx),
            'value': vx
        }

    def format_sql(self):
        # data {key: value} -> key = ? value_list -> [value1, value2, value3]
        if not hasattr(self, 'value') or self.value is None:
            self.data_decode()
        vk = self.value.get('key')
        if vk:
            self.sql_template = self.__sql_template.format(self.table, vk)
        if self.sql_template and self.where:
            self.sql_template += f' {self.where}'
        self.params = tuple(self.params)

class Select(SqlBase, TSelect, SqlWhere):

    def __init__(self, /, **kwargs):
        SqlBase.__init__(self)
        TSelect.__init__(self, **kwargs)
        SqlWhere.__init__(self)
        self.__sql_template = 'SELECT {} FROM {}'
        self.fields = []
        if kwargs.get('fields'):
            self.__set_fields(kwargs['fields'])
        else:
            self.fields = ['*']

    def __set_fields(self, fields):
        if not fields: return
        if isinstance(fields, str):
            self.fields = [fields]
            return
        if isinstance(fields, list):
            self.fields = fields
            return
        if isinstance(fields, tuple):
            self.fields = list(fields)
            return
        if isinstance(fields, dict):
            self.fields = [f'{k} AS {v}' for k, v in fields.items()]
            return

    def set_order(self, **kwargs):
        if not kwargs: return
        self.order = 'ORDER BY '
        _order = []
        for k, v in kwargs.items():
            # 0 升序 1 降序
            _order.append(f'{k} DESC' if v else f'{k} ASC')

        self.order += ','.join(_order)

    def set_limit(self, row: int = 0, num: int = 0):
        self.limit = f'LIMIT {num} OFFSET {row}'
        pass

    def set_join(self, *join_obj):
        """设置 连表对象
        Args:
            *join_obj (dict): 连表对象
                ### 示例
                ```python
                {
                    'keyword': 'left', # left right join
                    'sql': str(sql),
                    'table': str(table),
                    'table_as': str(t),
                    'col_key': str(col_name),
                    'col_value': str(table.col_name),
                }
                # 结果
                LEFT JOIN table as t ON
                ```
        """
        tmp = []
        if not join_obj: raise Error.ParamsError(400002)
        for obj in join_obj:
            if not isinstance(obj, dict): raise Error.ParamsError(400001)
            mod = obj.get('keyword')
            match mod:
                case 'left' | 'right':
                    mod = f'{mod.upper()} JOIN'
                case _:
                    mod = 'JOIN'
            if obj.get('on'):
                if 'sql' in obj:
                    tmp.append(f"{mod} ({obj['sql']}) AS {obj['table_as']} ON {' '.join(obj['on'])}")
                else:
                    tmp.append(f"{mod} {obj['table']} AS {obj['table_as']} ON {' '.join(obj['on'])}")
            else:
                if 'sql' in obj:
                    tmp.append(f"{mod} ({obj['sql']}) AS {obj['table_as']} ON {obj['col_key']} = {obj['col_value']}")
                else:
                    tmp.append(f"{mod} {obj['table']} AS {obj['table_as']} ON {obj['col_key']} = {obj['col_value']}")
        else:
            self.join = ' '.join(tmp)

    def set_group(self, *fields):
        if not fields: return
        f_l = []
        for f in fields:
            tmp = f.split('__', 1)
            if len(tmp) == 2:
                f_l.append(f'{tmp[0]}.{tmp[1]}')
            else:
                f_l.append(f'{tmp[0]}')
        else:
            self.group = f'GROUP BY {",".join(f_l)}'
        return self

    def format_sql(self):
        _sql = ''
        if self.table and self.fields:
            _sql = self.__sql_template.format(','.join(self.fields), self.table)
        if self.join:
            _sql += f' {self.join}'
        if self.where:
            _sql += f' {self.where}'
        if self.group:
            _sql += f' {self.group}'
        if self.order:
            _sql += f' {self.order}'
        if self.limit:
            _sql += f' {self.limit}'
        if _sql:
            if '?' in _sql:
                self.sql_template = _sql
            else:
                self.set_sql(_sql)
        return _sql

    def format_data(self, t = 'dict') -> list|dict:
        """格式化数据结果"""
        if not hasattr(self, 'data') or self.data is None:
            raise Error.UseError(200001)
        if not isinstance(self.data, dict):
            raise Error.ParamsError(400001)
        _d = dict(self.data)
        if 'field' in _d.keys() and 'data' in _d.keys():
            if t == 'dict':
                self.res = _data_dict(_d.get('field'), _d.get('data'))
            elif t == 'list':
                self.res = _data_table(_d.get('field'), _d.get('data'))
            else:
                raise Error.ParamsError(400004)
            return self.res
        else:
            raise Error.ParamsError(400003)

class DB(TDB):

    def __init__(self):
        TDB.__init__(self)
        self.db_type = 'sqlite3'
        self.db_info = {
            'database': None
        }
        import sqlite3
        self.device = sqlite3

    def run(self, sql: Select | Insert | Update | Delete):
        # sql 模板 str | list[str]
        if sql.sql_template:
            # sql 参数 dict | list[dict] -> dict: {template: str, params: list}
            sql_value = sql.get_values()
        else:
            # 纯字符串 sql
            sql_value = sql.get_sql()
        sql_type = sql.get_type()
        # 游标
        cursor = self.__db.cursor()

        if sql_type == 'query':
            try:
                if isinstance(sql_value, dict):
                    if isinstance(sql_value['params'], tuple):
                        cursor.execute(sql_value.get('template'), sql_value.get('params'))
                    if isinstance(sql_value['params'], list):
                        cursor.executemany(sql_value.get('template'), sql_value.get('params'))

                if isinstance(sql_value, str):
                    cursor.execute(sql_value)
            except Exception as e:
                raise Error.RunSqlError(100020, e)
            else:
                sql.data = {
                    'field': [i[0] for i in cursor.description],
                    'data': cursor.fetchall()
                }
        elif sql_type == 'affairs':
            if isinstance(sql_value, list):
                for i in sql_value:
                    if isinstance(i['params'], tuple):
                        cursor.execute(i.get('template'), i.get('params'))
                    if isinstance(i['params'], list):
                        cursor.executemany(i.get('template'), i.get('params'))

            if isinstance(sql_value, dict):
                if isinstance(sql_value['params'], tuple):
                    cursor.execute(sql_value.get('template'), sql_value.get('params'))
                if isinstance(sql_value['params'], list):
                    cursor.executemany(sql_value.get('template'), sql_value.get('params'))

            if isinstance(sql_value, str):
                cursor.execute(sql_value)

        else:
            raise Exception('sql type error')

    def rollback(self):
        self.__db.rollback()

    def commit(self):
        self.__db.commit()

    def set_conf(self, db_path):
        self.db_info['database'] = db_path

    def connect(self):
        """ 连接数据库"""
        self.__db = self.device.connect(self.db_info['database'])

    def close(self):
        self.__db.close()


__all__ = [
    'Insert',
    'Delete',
    'Update',
    'Select',
]
