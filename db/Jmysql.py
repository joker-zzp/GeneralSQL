from ..Template import *
from .. import Error
import datetime


def _data_dict(fields: tuple, datas: list) -> list:
    res = []
    keys = range(len(fields))
    for v in datas:
        tmp = {}
        for k in keys:
            tmp.update({fields[k]: str(v[k]) if isinstance(v[k], datetime.datetime) else v[k]})
        res.append(tmp)
    return res

def _data_table(fields: tuple, datas: list) -> dict:
    res = {
        'header': list(fields),
        'data': [[str(d) if isinstance(d, datetime.datetime) else d for d in i] for i in datas],
    }
    return res

def _format_field(field):
    # field = []
    res = []
    if isinstance(field, dict):
        for k, v in dict(field).items():
            tmp = k.split('__', 1)
            if len(tmp) == 2:
                if tmp[0]:
                    res.append(f'{tmp[0]}.`{tmp[1]}` AS `{v}`' if v else f'{tmp[0]}.`{tmp[1]}`')
                else:
                    res.append(f'{tmp[1]} AS `{v}`' if v else f'`{tmp[1]}`')
            else:
                # key 支持方法 去掉``包裹
                res.append(f'{k} AS `{v}`' if v else f'`{k}`')
    elif isinstance(field, (tuple, list)):
        res = [f'`{i}`' for i in list(field)]
    else:
        raise Error.ParamsError(400001)
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

class SqlWhere:

    def __init__(self):
        self.where = None

    # 设置条件
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

class DB(TDB):

    def __init__(self):
        TDB.__init__(self)
        self.db_type = 'mysql'
        self.db_info = {
            'database': None,
            'user': None,
            'passwd': None,
            'host': 'localhost',
            'port': 3306
        }
        import mysql.connector
        self.device = mysql.connector
        self.__init_conf = False
        self.__db = None

    def set_conf(self, **db_info):
        # up data key
        upkey = {
            'password': 'passwd'
        }
        for k, v in upkey.items():
            if db_info.get(k):
                db_info.update({v: db_info.pop(k)})
        need_key = [k for k, v in self.db_info.items() if v == None]
        if not set(db_info.keys()) >= set(need_key):
            raise Error.DatabaseConfError(100001, set(need_key) - set(db_info))
        # sign init conf
        self.db_info.update(db_info)
        self.__init_conf = True

    def run(self, sql):
        if sql != None and self.__connect:
            __type = sql.get_type()
            value = sql.get_sql()
            # 游标
            dbcursor = self.__db.cursor()
            if __type == 'query':
                try:
                    dbcursor.execute(value)
                except Exception as e:
                    raise Error.RunSqlError(100020, e)
                else:
                    sql.data = {
                        'field': dbcursor.column_names,
                        'data': dbcursor.fetchall()
                    }
            else:
                if isinstance(value, list):
                    for i in value:
                        try:
                            dbcursor.execute(i)
                        except Exception as e:
                            raise Error.RunSqlError(100020, e)
                else:
                    try:
                        dbcursor.execute(value)
                    except Exception as e:
                        raise Error.RunSqlError(100020, e)

    def commit(self):
        try:
            self.__db.commit()
        except Exception as e:
            raise Error.CommitError(100022, e)

    def rollback(self):
        try:
            self.__db.rollback()
        except Exception as e:
            raise Error.RollbackError(100023, e)

    def connect(self):
        # 检查 配置 初始化 通过
        if self.__init_conf:
            try:
                self.__db = self.device.connect(**self.db_info)
                self.__connect = True
            except self.device.errors.InterfaceError as e:
                raise Error.CommitError(100011, e)
            except Exception as e:
                raise Error.ConnectError(100010, e)
        else: raise Error.UseError(200001, 'conf not init, please use "set_conf" method.')

    def close(self):
        if self.__db:
            self.__db.close()
        else:
            raise Error.UseError(200001)

class Insert(TInsert):

    def __init__(self, table, data, update = False):
        TInsert.__init__(self, table, data)
        if isinstance(data, dict):
            self.fields = list(data.keys())
        elif isinstance(data, list) and  len(data) > 0:
            if isinstance(data[0], dict):
                # fixbug 当数据为列表时 有些数据有的字段没有时会丢失字段
                self.fields = list(set.union(*[set(i.keys()) for i in data]))
            else:
                Error.ParamsError(400001)
        else:
            Error.ParamsError(400001)
        self.__base = ['INSERT INTO', 'VALUES', 'ON DUPLICATE KEY UPDATE']
        self.val_max = 5
        self.values = []
        self.update = update

    def data_decode(self, data = None):
        if isinstance(self.data, dict) or data:
            data:dict = data if data else self.data
            # 循环 字段列表 数据中 不存在此key 并且 这个key的值不是 None 时 为这个值的数据 否则 为 null 关键字
            data_list = [repr(data.get(i)) if i in data.keys() and data.get(i) != None else 'NULL' for i in self.fields]
            self.values.append(f"({','.join(data_list)})")
        else:
            if isinstance(self.data, list):
                for i in self.data:
                    self.data_decode(i)
            else:
                raise Error.ParamsError(400001)

    def format_sql(self):
        if not self.values:
            self.data_decode()
        res = []
        field = ','.join([f'`{i}`' for i in self.fields])
        format_update = [f'{i}={self.__base[1]}({i})' for i in self.fields]
        for i in range(0, len(self.values), self.val_max):
            # 0:5, 5:10, 10:15 ...
            tmp = self.values[i: i + self.val_max]
            if self.update:
                # 重复更新
                res.append(f"{self.__base[0]} {self.table} ({field}) {self.__base[1]} {','.join(tmp)} {self.__base[2]} {','.join(format_update)}")
            else:
                res.append(f"{self.__base[0]} {self.table} ({field}) {self.__base[1]} {','.join(tmp)}")
        self.set_sql(res)

class Update(TUpdate, SqlWhere):

    def __init__(self, table, data):
        TUpdate.__init__(self, table, data)
        SqlWhere.__init__(self)
        self.__base = ['UPDATE', 'SET']

    def data_decode(self):
        if hasattr(self, 'data'):
            if isinstance(self.data, dict):
                self.value = [f'`{k}` = {v}' for k, v in self.data.items()]
            else:
                raise Error.ParamsError(400001)
        else:
            raise Error.UseError(200002)

    def set_where(self, *filters):
        return SqlWhere.set_where(self, *filters)

    def format_sql(self):
        self.data_decode()
        str_data = ','.join(self.value)
        sql = f'{self.__base[0]} {self.table} {self.__base[1]} {str_data}'
        if self.where:
            sql = f'{sql} {self.where}'
        self.set_sql(sql)

class Delete(TDelete, SqlWhere):

    def __init__(self, table):
        TDelete.__init__(self, table)
        SqlWhere.__init__(self)
        self.__base = ['DELETE FROM']

    def set_where(self, *filters):
        return SqlWhere.set_where(self, *filters)

    def format_sql(self):
        sql = f'{self.__base[0]} {self.table}'
        if self.where:
            sql = f'{sql} {self.where}'
        self.set_sql(sql)

class Select(TSelect, SqlWhere):

    def __init__(self, **kwargs):
        TSelect.__init__(self, **kwargs)
        SqlWhere.__init__(self)
        self.__base = ['SELECT', 'FROM']
        if kwargs.get('fields'):
            if isinstance(kwargs.get('fields'), (list, tuple, dict)):
                self.fields = _format_field(kwargs.get('fields'))
        else:
            self.fields = '*'

    def set_fields(self, *fields):
        if len(fields) < 1:
            raise Error.ParamsError(400002)
        for i in fields:
            self.fields = _format_field(i)

    def set_where(self, *filters):
        return SqlWhere.set_where(self, *filters)

    # 设置分组
    def set_group(self, *fields):
        '''
        Set up groups
            *fields: table field
                [field] or [table]__[field]
        '''
        if fields:
            f_list = []
            for i in fields:
                tmp = i.split('__', 1)
                f_list.append(f'{tmp[0]}.`{tmp[1]}`' if len(tmp) == 2 else f'`{i}`')
            if f_list:
                self.group = 'GROUP BY {}'.format(','.join(f_list))
        else:
            raise Error.ParamsError(400002)

    # 设置排序
    def set_order(self, **fields):
        """设置排序

        Raises:
            Error.ParamsError: _description_
        """
        if fields:
            f_list = []
            for k, v in fields.items():
                tmp = k.split('__', 1)
                if len(tmp) == 2:
                    f_list.append(f'{tmp[0]}.`{tmp[1]}` DESC' if v else f'{tmp[0]}.`{tmp[1]}`')
                else:
                    f_list.append(f'`{k}` DESC' if v else f'`{k}`')
            if f_list:
                self.order = 'ORDER BY {}'.format(','.join(f_list))
        else:
            raise Error.ParamsError(400002)

    # 设置分页
    def set_limit(self, row, num = None):
        if isinstance(row, int):
            self.limit = f'LIMIT {row}'
        else:
            raise Error.ParamsError(400001)
        if isinstance(num, int):
            self.limit = f'{self.limit}, {num}'
        else:
            if num != None:
                raise Error.ParamsError(400001)

    # 设置链表查询
    def set_join(self, *join_obj) -> str:
        '''
        set join sql object
            *join_obj: Join table object
                {
                    'keyword': ['join', 'left', 'right'],
                    'sql': str(sql),
                    'table': str(table_name),
                    'table_as': str(t),
                    'col_key': str(col_name),
                    'col_value': str(table.col_name),
                }
        '''
        tmp = []
        if join_obj:
            for obj in join_obj:
                mod = None
                if obj.get('keyword').lower() == 'left':
                    mod = 'LEFT JOIN'
                elif obj.get('keyword').lower() == 'right':
                    mod = 'RIGHT JOIN'
                elif obj.get('keyword').lower() == 'join':
                    mod = 'JOIN'
                else:
                    raise Error.ParamsError(400003, 'keyword not in ["join", "left", "right"]')
                if obj.get('on'):
                    if 'sql' in join_obj:
                        tmp.append(f"{mod} ({str(obj['sql'])}) {str(obj['table_as'])} ON {' '.join(obj['on'])}")
                    else:
                        tmp.append(f"{mod} {str(obj['table'])} {str(obj['table_as'])} ON {' '.join(obj['on'])}")
                else:
                    if 'sql' in join_obj:
                        tmp.append(f"{mod} ({str(obj['sql'])}) {str(obj['table_as'])} ON {str(obj['table_as'])}.`{obj['col_key']}` = {str(obj['col_value'])}")
                    else:
                        tmp.append(f"{mod} {str(obj['table'])} {str(obj['table_as'])} ON {str(obj['table_as'])}.`{obj['col_key']}` = {str(obj['col_value'])}")
        else:
            raise Error.ParamsError(400002)
        if tmp:
            self.join = ' '.join(tmp)

    def format_sql(self):
        sql = ''
        if self.table and self.fields:
            if isinstance(self.table, dict):
                self.table = [f'{k} {v}' for k, v in self.table.items()]
            elif isinstance(self.table, str):
                self.table = [self.table]
            table = ','.join(self.table)
            field = ','.join(self.fields)
            sql = f'{self.__base[0]} {field} {self.__base[1]} {table}'
            if self.join:
                sql = f'{sql} {self.join}'
            if self.where:
                sql = f'{sql} {self.where}'
            if self.group:
                sql = f'{sql} {self.group}'
            if self.order:
                sql = f'{sql} {self.order}'
            if self.limit:
                sql = f'{sql} {self.limit}'
            self.set_sql(sql)
        else:
            raise Error.ParamsError(400002)

    def format_data(self, t = 'dict') -> list|dict:
        """格式化数据结果

        Args:
            t (str, optional): 模板. Defaults to 'dict'.

        Raises:
            Error.UseError: 参数异常 对象必须有 data 属性

        Returns:
            list|dict: 结果
        """
        # 检查数据是否存在
        if not hasattr(self, 'data'):
            raise Error.UseError(200001)
        if 'field' in self.data.keys() and 'data' in self.data.keys():
            if t == 'dict':
                self.res = _data_dict(self.data.get('field'), self.data.get('data'))
            elif t == 'table':
                self.res = _data_table(self.data.get('field'), self.data.get('data'))
            return self.res

__all__ = [
    'Insert',
    'Select',
    'Update',
    'Delete',
]
