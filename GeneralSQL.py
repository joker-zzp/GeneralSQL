from .senior import Insert, Delete, Update, Select
from . import Error

class SeniorSQL(Select, Insert, Update, Delete):
    '''
    General Senior Class
    
    Here you inherit the base package and override the base class methods
    '''

    def __init__(self):
        self.table = None
        self.field = None
        self.join = None
        self.where = ''
        self.group_by = None
        self.order_by = None
        self.limit = None

    # 添加
    def Add(self, table, field_list, dict_data_list):
        ''' 
        Insert function 插入数据方法

            table (表) -> str
            field_list (字段) -> list
            data (数据) -> list(dict)
        '''
        Insert.__init__(self, table)
        Insert.set_field_list(self, field_list)
        Insert.set_data(self, dict_data_list)
        sql_list = Insert.format_sql(self)
        return sql_list

    # 删除
    def Del(self, table):
        '''
        Delete function 删除方法

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
        '''
        Updata function 更新方法

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
        '''
        Select function 查询方法

            table (表) -> str|dict
            field (字段) -> list|dict
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

    # 格式化条件
    def fomat_filter(self, symbol, _table_as = None, _not = False, _factor = None, **col_value) -> str:
        '''
        Filters for where conditions

            symbol: '=' Recognizable symbols ['=', '<=', '>=', '!=', '<>', '<', '>', ' in', 'isnull', 'between']
            _table_as: Table alternative name
            _not: [default](False) 取反 --> sql not
            _factor: [default](None) Value range --> ('and' | 'or')
            **col_value:
                explain: 字典化 一般常用 写法 字段名 = 条件
                for example:
                    [object].fomat_filter(symbol='IN', id=[1,2,3]) return: `id` IN ("1","2","3")
                    [object].fomat_filter(symbol='between',_not=True, id={'start': 1, 'end': 10}) return: `id` NOT BETWEEN "1" AND "10"
                    [object].fomat_filter(symbol='<',_not=True,_factor='and', id=10) return: AND NOT `id` < 10
                    [object].fomat_filter(symbol='isnull',_not=True, cok='name') return: NOT ISNULL(`name`)
                    [object].fomat_filter(symbol='like',_not=True, name='') return: NOT ISNULL(`name`)
        '''
        if col_value:
            if len(col_value) > 1:
                raise Error.TooManyParamErr(*col_value)
            symbol_list = ['=', '<=', '>=', '!=', '<>', '<', '>', 'IN', 'LIKE', 'BETWEEN', 'ISNULL']
            if symbol.upper() in symbol_list:
                result = ''
                col = list(col_value.keys())[0]
                if _table_as:
                    col = f'{_table_as}.`{col}`'
                value = list(col_value.values())[0]
                if symbol.upper() == 'ISNULL':
                    if isinstance(value, str):
                        if _not:
                            result = 'NOT ISNULL({val})'.format(val=col)
                        else:
                            result = 'ISNULL({val})'.format(val=col)
                elif symbol.upper() == 'IN':
                    if _not:
                        result = '{col} NOT IN ("{val}")'.format(col = col, val = '","'.join([str(i) for i in value]))
                    else:
                        result = '{col} IN ("{val}")'.format(col = col, val = '","'.join([str(i) for i in value]))
                elif symbol.upper() == 'LIKE':
                    if _not:
                        result = '{col} NOT LIKE "{val}"'.format(col = col, val = str(value))
                    else:
                        result = '{col} LIKE "{val}"'.format(col = col, val = str(value))
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

    # 追加条件
    def where_append(self, *filters):
        if filters:
            self.where += ' {}'.format(' '.join(filters))
        else:
            raise Error.ParamMiss('filter')

    # 获取查询条件
    def get_where(self) -> str:
        ''' Get object 'where' condition
        '''
        return self.where

    # 设置分组
    def set_group_by(self, *fields):
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
                self.group_by = 'GROUP BY {}'.format(','.join(f_list))
        else:
            raise Error.ParamMiss('fields')

    # 获取分组
    def get_group_by(self) -> str:
        """
        Get group
        """
        return self.group_by

    # 设置排序
    def set_order_by(self, **fields):
        '''
        Set sort
            **fields: table field, value=[ 1:DESC or 0:ASC ]
                [field]=1 or [table]__[field]=1
        '''
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
        else:
            raise Error.ParamMiss('fields')

    # 获取排序
    def get_order_by(self) -> str:
        """
        Get sort
        """
        return self.order_by

    # 设置分页
    def set_limit(self, rows, num = None):
        '''
        Set paging
            rows: start Number
            num: Number of data
        '''
        if isinstance(rows, int) and isinstance(num, int):
            self.limit = f'LIMIT {rows}, {num}'
        elif isinstance(int(rows)):
            self.limit = f'LIMIT {rows}'
        else:
            if not num:
                raise Error.ParamTypeNotSupported(rows)
            raise Error.ParamTypeNotSupported(rows, num)

    # 获取分页
    def get_limit(self) -> str:
        """
        Get paging
        """
        return self.limit

    # 设置联表对象
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
                if obj['keyword'].lower() == 'left':
                    obj['keyword'] = 'LEFT JOIN'
                elif obj['keyword'].lower() == 'right':
                    obj['keyword'] = 'RIGHT JOIN'
                elif obj['keyword'].lower() == 'join':
                    obj['keyword'] = 'JOIN'
                else:
                    raise Error.ParamTypeNotSupported(obj['keyword'])
                if 'sql' in join_obj:
                    tmp.append(f"{str(obj['keyword'])} ({str(obj['sql'])}) {str(obj['table_as'])} ON {str(obj['table_as'])}.`{obj['col_key']}` = {str(obj['col_value'])}")
                else:
                    tmp.append(f"{str(obj['keyword'])} {str(obj['table'])} {str(obj['table_as'])} ON {str(obj['table_as'])}.`{obj['col_key']}` = {str(obj['col_value'])}")
        else:
            raise Error.NoObject('join_obj')
        if tmp:
            self.join = ' '.join(tmp)

    # 获取联表对象
    def get_join(self) -> str:
        '''
        get join sql object
        '''
        return self.join
    
    # 获取对应方法sql
    def get_func_sql(self, func):
        '''
        Get func sql
        获取对应方法的 SQL

            func: [sel, add, up, del]
        '''
        if func.upper() == 'SEL':
            if self.join:
                Select.set_sql(self, f'{Select.get_sql(self)} {self.join}')
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
            return Insert.get_sql_list(self)
        elif func.upper() == 'UP':
            if self.where:
                Update.set_sql(self, f'{Update.get_sql(self)} {self.where}')
                return Update.get_sql(self)
        elif func.upper() == 'DEL':
            if self.where:
                Delete.set_sql(self, f'{Delete.get_sql(self)} {self.where}')
                return Delete.get_sql(self)
        else:
            raise Error.ParamTypeNotSupported(func)

    # 获取结果
    def get_result(self, func, _format = 'dict'):
        if func.upper() == 'SEL':
            if _format in ['dict', 'template']:
                return Select.get_result(self, format=_format)
