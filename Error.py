# code and message
Error_code_msg = {
    # 测试
    000000: {'code': 000000, 'message': 'Test Error !'},
    # 1 类 - 代码错误
    100001: {'code': 100001, 'message': 'object type is not %s !'},
    100002: {'code': 100002, 'message': 'object miss param "%s" !'},
    100003: {'code': 100003, 'message': 'No %s objects available !'},
    100004: {'code': 100004, 'message': 'This symbol "%s" Unrecognized !'},
    100005: {'code': 100005, 'message': 'Too many parameters to process !'},
    100006: {'code': 100006, 'message': 'Parameter "%s" type not supported !'},
    100007: {'code': 100007, 'message': 'The %s type does not support the current format !'},
    # 2 类 - 数据库错误
    200001: {'code': 200001, 'message': 'Databese "%s"@"%s".%s connection is Error, post: %s !'},
    200002: {'code': 200002, 'message': 'Commit Failed !'},
    # 3 类 - 数据错误
    300001: {'code': 300001, 'message': 'Failed to set transaction !'},
    300002: {'code': 300002, 'message': 'SQL setting error !'},
    300003: {'code': 300003, 'message': 'SQL type error !'},
}

def getCodeMsg(code):
    return Error_code_msg[code]['code'], Error_code_msg[code]['message']

res = lambda x: '\ncode: {} -> "{}": {}'.format(*x)

class GeneralSqlError(Exception):

    def __init__(self, *args):
        self.args = args

# Test

class TestErr(GeneralSqlError):
    def __init__(self):
        self.code, self.message = getCodeMsg(000000)
        
    def __str__(self):
        return res([self.code, 'J\' test !', self.message])

# 1 类 - 代码错误

# 类型错误
class TypeErr(GeneralSqlError):
    def __init__(self, *args, **kwages):
        super().__init__(*args)
        self.this_type = kwages['this_type']
        self.code, self.message = getCodeMsg(100001)
    
    def __str__(self):
        return res([self.code, self.args, self.message%(self.this_type)])

# 符号错误
class SymbolErr(GeneralSqlError):
    def __init__(self, symbol, *args):
        super().__init__(*args)
        self.symbol = symbol
        self.code, self.message = getCodeMsg(100004)

    def __str__(self):
        return res([self.code, self.symbol, self.message%(self.symbol)])

# 缺少参数
class ParamMiss(GeneralSqlError):
    def __init__(self, param, *args):
        super().__init__(*args)
        self.param = param
        self.code, self.message = getCodeMsg(100002)

    def __str__(self):
        return res([self.code, self.args[0], self.message%(self.param)])

# 参数类型不支持
class ParamTypeNotSupported(GeneralSqlError):
    def __init__(self, *args):
        self.code, self.message = getCodeMsg(100006)

    def __str__(self):
        return res([self.code, self.args, self.message%(type(self.args[0]))])

# 参数太多
class TooManyParamErr(GeneralSqlError):
    def __init__(self):
        self.code, self.message = getCodeMsg(100005)

    def __str__(self):
        return res([self.code, self.args, self.message])

# 没有对象
class NoObject(GeneralSqlError):
    def __init__(self, object_name, *args):
        super().__init__(*args)
        self.object_name = object_name
        self.code, self.message = getCodeMsg(100003)

    def __str__(self):
        return res([self.code, self.args, self.message%(self.object_name)])

# 数据类型错误
class DataTypeErr(GeneralSqlError):
    def __init__(self, data_tpye, *args):
        super().__init__(*args)
        self.data_tpye = data_tpye
        self.code, self.message = getCodeMsg(100007)

    def __str__(self):
        return res([self.code, self.args, self.message%(self.data_tpye)])


# 2 类 - 数据库错误

# 数据库连接失败
class DatabaseConnectionErr(GeneralSqlError):
    def __init__(self, *args, **kwages):
        super().__init__(*args)
        self.kwages = kwages
        self.code, self.message = getCodeMsg(200001)

    def __str__(self):
        return res([self.code, self.args, self.message%(self.kwages['username'], self.kwages['host'], self.kwages['database'], self.kwages['post'])])

# 提交事务失败
class CommitErr(GeneralSqlError):
    def __init__(self, *args):
        super().__init__(*args)
        self.code, self.message = getCodeMsg(200002)

    def __str__(self):
        return res([self.code, self.args, self.message])

# 3 类 - 数据错误

# Sql 类型错误
class SetAffairsErr(GeneralSqlError):
    def __init__(self, *args):
        super().__init__(*args)
        self.code, self.message = getCodeMsg(300001)
    
    def __str__(self):
        return res([self.code, self.args, self.message])

class SetSelectErr(GeneralSqlError):
    def __init__(self, *args):
        super().__init__(*args)
        self.code, self.message = getCodeMsg(300002)
    
    def __str__(self):
        return res([self.code, self.args, self.message])

class SqlTypeErr(GeneralSqlError):
    def __init__(self, *args):
        super().__init__(*args)
        self.code, self.message = getCodeMsg(300003)
    
    def __str__(self):
        return res([self.code, self.args, self.message])
