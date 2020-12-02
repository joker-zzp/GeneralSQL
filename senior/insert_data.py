from .base.my_sql import Run_Sql
from .. import Error

class Insert(Run_Sql):
    
    def __init__(self, table, val_max = 50):
        self.base = ['INSERT INTO', 'VALUES']
        self.table = table
        self.field_list = []
        self.data = {}
        self.sql_list = []
        self.val_max = 50

    def __format_sql(self, data):
        ''' Format Insert sql

            data (数据) -> dict/list/
        '''
        if self.table and self.field_list and data:
            format_dic_data = lambda key_list, value: [f'"{(value.get(i[1:-1]))}"' for i in key_list]
            if isinstance(data, dict):
                tmp = ','.join(format_dic_data(self.field_list, data))
                data = f'({tmp})'
            else:
                tmp_str = lambda x : ','.join(format_dic_data(self.field_list, x))
                tmp = [f'({tmp_str(i)})' for i in data]
                data = ','.join(tmp)
            sql = '{into} {table}({field}) {val} {data}'.format(
                into = self.base[0],
                table = self.table,
                field = ','.join(self.field_list),
                val = self.base[1],
                data = data
            )
            return sql

    # 设置字段列表
    def set_field_list(self, field_list) -> list:
        ''' Set field list

            filed_list: 要添加数据的字段
        '''
        self.field_list = [f'`{i}`' for i in field_list]
        return self.field_list

    # 设置数据
    def set_data(self, data):
        self.data = data
        return self.data

    def format_sql(self):
        '''Format SQL statement
        '''
        if isinstance(self.data, dict):
            self.sql_list.append(self.__format_sql(self.data))
        elif isinstance(self.data, list):
            if len(self.data) <= self.val_max:
                self.sql_list.append(self.__format_sql(self.data))
            else:
                data = self.data.copy()
                cont = lambda x, max: len(x) // max + 1 if len(x) % max else len(x) // max
                for i in range(cont(data, self.val_max)):
                    start_index, end_index = (i * self.val_max, i * self.val_max + self.val_max -1)
                    tmp_data = data[start_index: end_index]
                    self.sql_list.append(self.__format_sql(tmp_data))
            return self.sql_list
        else: raise Error.ParamTypeNotSupported(self.data)

    def get_sql_list(self):
        return self.sql_list

    def get_insert_data(self):
        count = 0
        for i in self.sql_list:
            self.set_sql(i)
            # print(self.get_sql())
            self.get_data()
            count += self.get_format_data()['count']
        return count