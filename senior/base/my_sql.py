from datetime import datetime
import mysql.connector
from ... import Error

class Sql(object):

    def __init__(self):
        self.__type = ''
        self.__value = ''

    # 获取 sql 类型
    def get_sql_type(self) -> str:
        self.check_sql()
        return self.__type

    # 获取sql
    def get_sql(self) -> str:
        return self.__value 

    # 设置sql
    def set_sql(self, sql):
        if not isinstance(sql, str):
            raise Error.ParamTypeNotSupported(sql)
        self.__value = sql
        return

    # 检查SQL类型
    def check_sql(self) -> str:
        type_dic = {'select': 'query', 'show': 'query', 'field': 'query', 'desc': 'query', 'insert': 'affairs', 'update': 'affairs', 'delete': 'affairs'}
        sql_type = lambda x: type_dic.get(x) if type_dic.get(x) else ''
        self.__type =  sql_type(self.__value.split()[0].lower())
        if not self.__type:
            raise Error.ParamTypeNotSupported(*type_dic)
        return self.__type


class Run_Sql(Sql):
    __DB_Info__ = {
        'database': None,
        'user': None,
        'passwd': None,
        'host': 'localhost',
        'port': 3306,
    }
    __data = {}

    def __init__(self):
        self.__db = None

    # 设置 数据库连接参数
    def set_db_info(self, **kwargs):
        if kwargs:
            if 'user' in kwargs.keys():
                self.__DB_Info__['user'] = kwargs['user']
            else:
                raise Error.ParamMiss(self, 'user')
            if 'password' in kwargs.keys():
                self.__DB_Info__['passwd'] = kwargs['password']
            else:
                raise Error.ParamMiss(self, 'password')
            if 'host' in kwargs.keys():
                self.__DB_Info__['host'] = kwargs['host']
            if 'database' in kwargs.keys():
                self.__DB_Info__['database'] = kwargs['database']
            if 'port' in kwargs.keys():
                self.__DB_Info__['port'] = kwargs['port']
        else:
            raise Error.ParamMiss(self,['database', 'user', 'password'])
        # test connect
        try:
            self.__db = mysql.connector.connect(**self.__DB_Info__)
            return 1
        except Exception as e:
            print(e)

    def get_db_info(self):
        return self.__DB_Info__

    def commit(self):
        try:
            self.__db.commit()
        except Exception as e:
            self.__data['count'] = 0
            raise Error.CommitErr(*e.args)

    # 回滚 roolback
    def rollback(self):
        try:
            self.__db.rollback()
        except Exception as e:
            # self.__data['count'] = 0
            raise Error.CommitErr(*e.args)

    # 关闭数据库
    def close(self):
        self.__db.close()

    # 运行sql
    def __run(self) -> dict:
        ''' run
        '''
        if self.__db:
            self.__data = {}
            dbcursor = self.__db.cursor()
            sql_type = self.get_sql_type()
            if sql_type:
                if sql_type == 'query':
                    try:
                        # print(self.get_sql())
                        dbcursor.execute(self.get_sql())
                    except Exception as e: raise Error.SetSelectErr(*e.args)
                    self.__data = {'field': dbcursor.column_names,'data': dbcursor.fetchall()}
                    self.__data['count'] = len(self.__data['data'])
                else:
                    try:
                        dbcursor.execute(self.get_sql())
                    except Exception as e: raise Error.SetAffairsErr(*e.args)
                    self.__data['count'] = dbcursor.rowcount
            else:
                raise Error.SqlTypeErr(self.get_sql())
        else:
            raise Error.NoObject('database')

    # 获取数据原型
    def get_data(self) -> dict:
        self.__run()
        return self.__data

    # 获取 JSON 格式数据
    def get_format_data(self) -> dict:
        if self.get_sql_type() == 'affairs':
            return self.__data
        elif self.get_sql_type() == 'query':
            return self.__format_data()
        else:
            return {}

    # 获取 列表化数据
    def get_template_data(self) -> list:
        sql_type = self.get_sql_type()
        if sql_type == 'query':
            return self.__template_data()
        else:
            raise Error.DataTypeErr(sql_type, self.get_sql())

    # Format data to list[dict]
    def __format_data(self) -> list:
        init_data = []
        key = [i for i in self.__data['field']]
        for i in self.__data['data']:
            one_data = {}
            for f in range(len(key)):
                one_data[key[f]] = self.__date_str(i[f])
            init_data.append(one_data)
        return init_data

    # Template data dict{'field': list[], 'data': list[]}
    def __template_data(self) -> dict:
        init_data = {}
        if self.__data:
            if self.__data['field']:
                init_data['field'] = [i[0] for i in self.__data['field']]
            init_data['data'] = [self.__date_str(list(i)) for i in self.__data['data']]
        return init_data

    # date_time -> str
    @staticmethod
    def __date_str(data):
        str_data = lambda x: str(x) if isinstance(x, type(datetime.now())) else x
        if isinstance(data, list):
            return [ str_data(i) for i in data]
        else:
            return str_data(data)
