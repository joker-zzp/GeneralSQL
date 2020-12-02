from .base.my_sql import Run_Sql

class Update(Run_Sql):
    
    def __init__(self, table):
        self.base = ['UPDATE', 'SET']
        self.table = table
        self.data = {}
        self.data_list = []

    def set_data(self, data):
        f_data = lambda k, v: f'{k}={v}' if isinstance(v, str) and v.upper() == 'NULL' else f'{k}="{v}"'
        self.data_list = [f_data(k, v) for k, v in data.items()]
        return self.data_list

    def format_sql(self):
        str_data = ','.join(self.data_list)
        self.set_sql(f'{self.base[0]} {self.table} {self.base[1]} {str_data}')
        return self.get_sql()