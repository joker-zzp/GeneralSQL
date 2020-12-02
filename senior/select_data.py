from .base.my_sql import Run_Sql
from .. import Error

class Select(Run_Sql):
    """ Query SQL statement format.

        Attributes:
            'object.table' set a table name, stype is str
    """
    def __init__(self, table):
        self.base = ['SELECT', 'FROM']
        self.field = []
        self.table = table

    def format_sql(self):
        if self.field and self.table:
            if isinstance(self.table, dict):
                tables = dict(self.table).copy()
                self.table = []
                for k, v in tables.items():
                    tmp = f'{k} {v}' if v else f'{k}'
                    self.table.append(tmp)
                self.table = ','.join(self.table)
            sql = '{s} {col} {f} {tab}'.format(
                s   = self.base[0],
                col = ','.join(self.field),
                f   = self.base[1],
                tab = self.table
            )
        return sql

    def format_field(self, field):
        # col = []
        if isinstance(field, dict):
            for k, v in dict(field).items():
                tmp = k.split('__', 1)
                if len(tmp) == 2:
                    self.field.append(f'{tmp[0]}.`{tmp[1]}` AS `{v}`' if v else f'{tmp[0]}.`{tmp[1]}`')
                else:
                    self.field.append(f'`{k}` AS `{v}`' if v else f'`{k}`')
        elif isinstance(field, tuple):
            self.field = list(field)
            return self.field
        else:
            raise Error.ParamMiss('field')
    
    def set_field(self, field):
        self.field = field

    # 获取结果
    def get_result(self, format = 'dict'):
        """ Get result data

        Args:
            format: 'dict' Set get data format to 'Dict' by default

        Returns:
            Return result set, 'dict' or 'template' format.
        """
        if format == 'template':
            return Run_Sql.get_template_data(self)
        elif format == 'dict':
            return Run_Sql.get_format_data(self)
