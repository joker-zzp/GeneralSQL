# 基础数据 --> 增，删，改，查
from .senior.insert_data import Insert
from .senior.delete_data import Delete
from .senior.update_data import Update
from .senior.select_data import Select
from . import Error

class SeniorData(Select, Insert, Update):

    # __base_format_field = lambda x: [f'`{i}`' for i in x]

    def __init__(self):
        self.table = None
        self.field = None
        self.where = ''
        self.group_by = None
        self.order_by = None
        self.limit = None

    # 添加
    def Add(self, table, field_list, dict_data_list):
        ''' Insert function 插入数据方法

            table (表) -> str
            field_list (字段) -> list
            data (数据) -> list(dict)
        '''
        print(field_list)
        # self.table = table
        Insert.__init__(self, table)
        Insert.set_field_list(self, field_list)
        Insert.set_data(self, dict_data_list)
        sql_list = Insert.format_sql(self)
        return sql_list

    # 删除
    def Del(self, table):
        '''Delete function 删除方法

            table (表) -> str
        '''
        if table:
            Delete.__init__(self, table)
            Delete.format_sql(self)
            return self
        else:
            raise Error.ParamMiss('table')

    # 更新
    def Up(self, table, **data):
        '''Updata function 更新方法

            table (表) -> str

            data (数据) -> dict
        '''
        if data:
            Update.__init__(self, table)
            Update.set_data(self, data)
            Update.format_sql(self)
            return self
        else:
            raise Error.ParamMiss('data')


    # 查询
    def Sel(self, table, *field_list, **field):
        ''' Select function 查询方法

                field (字段) -> list

                table (表) -> str|dict
        '''
        Select.__init__(self, table)
        if field_list:
            Select.format_field(self, field_list)
        elif field:
            Select.format_field(self, dict(field))
        else:
            raise Error.ParamMiss('field')
        sql = Select.format_sql(self)
        self.set_sql(sql)
        return self

    # 获取表
    def get_table(self):
        return self.table

    # 获取字段
    def get_field(self):
        return self.field

    # 设置查询条件
    def set_where(self, *filters):
        """ Set criteria for the query

            filter: condition.
        """
        if filters:
            self.where = 'WHERE {}'.format(' '.join(filters))
        else:
            raise Error.ParamMiss('filter')

    # 获取查询条件
    def get_where(self) -> str:
        ''' Get object 'where' condition
        '''
        return self.where

    # 格式化条件
    def fomat_filter(self, symbol, _table_as = None, _not = False, _factor = None, **col_value) -> str:
        ''' 格式化 where 条件

            symbol: '=' Recognizable symbols ['=', '<=', '>=', '!=', '<>', '<', '>', ' in', 'isnull', 'between']
            _not: [default](False) 取反 --> sql not
            _factor: [default](None) Value range --> ('and' | 'or')
            **col_value:
                explain: 字典化 一般常用 写法 字段名 = 条件
                for example:
                    [object].fomat_filter(symbol='IN', id=[1,2,3]) return: `id` IN ("1","2","3")
                    [object].fomat_filter(symbol='between',_not=True, id={'start': 1, 'end': 10}) return: `id` NOT BETWEEN "1" AND "10"
                    [object].fomat_filter(symbol='<',_not=True,_factor='and', id=10) return: AND NOT `id` < 10
                    [object].fomat_filter(symbol='isnull',_not=True, cok='name') return: NOT ISNULL(`name`)
        '''
        if col_value:
            if len(col_value) > 1:
                raise Error.TooManyParamErr(*col_value)
            symbol_list = ['=', '<=', '>=', '!=', '<>', '<', '>', 'IN', 'BETWEEN', 'ISNULL']
            if symbol.upper() in symbol_list:
                result = ''
                col = list(col_value.keys())[0]
                if _table_as:
                    col = f'{_table_as}.`{col}`'
                value = list(col_value.values())[0]
                if symbol.upper() == 'ISNULL':
                    if isinstance(value, str):
                        if _not:
                            result = 'NOT ISNULL({val})'.format(val=value)
                        else:
                            result = 'ISNULL({val})'.format(val=value)
                    elif isinstance(value, [list, tuple]):
                        if _table_as:
                            value = [f'{_table_as}.`{i}`' for i in value]
                        else:
                            value = [f'`{i}``' for i in value]
                        value = ','.join(value)
                        if _not:
                            result = 'NOT ISNULL({val})'.format(val=value)
                        else:
                            result = 'ISNULL({val})'.format(val=value)
                elif symbol.upper() == 'IN':
                    if _not:
                        result = '{col} NOT IN ("{val}")'.format(col = col, val = '","'.join([str(i) for i in value]))
                    else:
                        result = '{col} IN ("{val}")'.format(col = col, val = '","'.join([str(i) for i in value]))
                elif symbol.upper() == 'BETWEEN':
                    if dict(value).get('start') and dict(value).get('end'):
                        if _not:
                            result = '{col} NOT BETWEEN "{start}" AND "{end}"'.format(col=col, start=value['start'], end=value['end'])
                        else:
                            result = '{col} BETWEEN "{start}" AND "{end}"'.format(col=col, start=str(value['start']), end=str(value['end']))
                    else: raise Error.ParamMiss('(start , end)', value)
                else:
                    if _not:
                        result = 'NOT {col} {symbol} "{val}"'.format(col=col, symbol=symbol, val=value)
                    else:
                        result = '{col} {symbol} "{val}"'.format(col=col, symbol=symbol, val=value)
                if _factor and _factor.upper() in ['AND', 'OR']:
                    result = '{} {}'.format(_factor.upper(), result)
                return result
            else:
                raise Error.SymbolErr(symbol)
        else:
            raise Error.ParamMiss('col_value')

    def set_group_by(self, *fields):
        if fields:
            f_list = []
            for i in fields:
                tmp = i.split('__', 1)
                f_list.append(f'{tmp[0]}.`{tmp[1]}`' if len(tmp) == 2 else f'`{i}`')
            if f_list:
                self.group_by = 'GROUP BY {}'.format(','.join(f_list))
            return self.group_by
        else:
            raise Error.ParamMiss('fields')

    def set_order_by(self, **fields):
        if fields:
            f_list = []
            for k, v in fields.items():
                tmp = k.split('__', 1)
                if len(tmp) == 2:
                    f_list.append(f'{tmp[0]}.`{tmp[1]}` DESC' if v else f'{tmp[0]}.`{tmp[1]}`')
                else:
                    f_list.append(f'`{k}` DESC' if v else f'`{k}`')
            if f_list:
                self.order_by = 'ORDER BY {}'.format(','.join(f_list))
            return self.order_by
        else:
            raise Error.ParamMiss('fields')

    # 设置分页
    def set_limit(self, rows, num = None):
        if isinstance(rows, int) and isinstance(num, int):
            print(1)
            self.limit = f'LIMIT {rows}, {num}'
            return self.limit
        elif isinstance(int(rows)):
            self.limit = f'LIMIT {rows}'

    def set_join(self):...

    def get_func_sql(self, func):
        if func.upper() == 'SEL':
            if self.where:
                Select.set_sql(self, f'{Select.get_sql(self)} {self.where}')
            if self.group_by:
                Select.set_sql(self, f'{Select.get_sql(self)} {self.group_by}')
            if self.order_by:
                Select.set_sql(self, f'{Select.get_sql(self)} {self.order_by}')
            if self.limit:
                Select.set_sql(self, f'{Select.get_sql(self)} {self.limit}')
            return Select.get_sql(self)
        elif func.upper() == 'ADD':
            return Insert.get_sql(self)
        elif func.upper() == 'UP':
            if self.where:
                Update.set_sql(self, f'{Update.get_sql(self)} {self.where}')
        elif func.upper() == 'DEL':
            if self.where:
                Delete.set_sql(self, f'{Delete.get_sql(self)} {self.where}')

    def get_result(self, func, _format = 'dict'):
        if func.upper() == 'SEL':
            if _format == 'dict':
                return Select.get_result(self)