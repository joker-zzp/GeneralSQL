# Error
# 1----- 数据库相关异常
# 2----- 类使用方法异常
# 3----- 方法运行异常
# 4----- 输入异常
# 5----- 输出处理异常

message = {
    # 未知异常
    000000: 'Unknown exception.',
    # 数据库相关异常
    # 数据库 配置参数 缺少
    100001: 'Missing database conf params.',
    # 数据库 配置参数异常
    100002: 'Database conf params error.',
    # 数据库 连接失败
    100010: 'Database connection failed.',
    # 数据库 无法连接mysql服务
    100011: 'Can\'t connect to MySQL server.',
    # 数据库 连接超时
    100012: 'Database connection timeout.',
    # 执行 sql 异常
    100020: 'Run SQL Exception.',
    # 执行 sql 超时
    100021: 'SQL execution timeout.',
    # 提交 错误
    100022: 'Submission failed.',
    # 回滚 错误
    100023: 'Rollback failed.',

    # 类使用方法异常
    # 对象 不能使用此方法
    200001: 'This object cannot use this method.',
    # 对象没有这个属性
    200002: 'The object dost not have the attribute.',
  
    # 方法运行异常
    # 模板格式化错误
    300001: 'Template format error.',
    # 输入异常
    
    # 参数异常
    400001: 'Params type error.',
    400002: 'Params miss.',
    400003: 'Params format error.',
    400004: 'Params value error.',
    
    # 输出异常
    # 结果处理异常
    500000: 'Result processing error.',
}

class BaseError(Exception):

    def __init__(self, code = 000000, /, *args):
        # 检查 code 是否存在
        self.code = code if code in message.keys() else 000000
        self.msg = message.get(self.code)
        self.res = Exception(*args)
        self.__str__()
    
    def __str__(self):
        return f'[{self.code:0>6}] [{self.__class__.__name__}] -> {self.msg}\nErrorMessage: {self.res}'

# test
class TestError(BaseError):...

# 数据库相关异常
class DatabaseConfError(BaseError):...
class ConnectError(BaseError):...
class RunSqlError(BaseError):...
class RunSqlTimeoutError(BaseError):...
class CommitError(BaseError):...
class RollbackError(BaseError):...
# 代码错误
class UseError(BaseError):...
class ParamsError(BaseError):...
class FormatError(BaseError):...

__all__ = [
    'ConnectError'
    'UseError'
    'TestError'
    'ParamsError'
    'FormatError'
]
