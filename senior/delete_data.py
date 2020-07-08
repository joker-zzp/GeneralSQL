from .base.my_sql import Run_Sql

class Delete(Run_Sql):
    
    def __init__(self, table):
        self.base = ['DELETE FROM']
        self.table = table

    def format_sql(self):
        self.set_sql(f'{self.base[0]} {self.table}')