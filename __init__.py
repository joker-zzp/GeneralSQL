# General sql 支持数据库 [MySQL, Mariadb]
# 基于 mysql-connector 进行开发
from .GeneralSQL import SeniorSQL

try:
    import mysql.connector
except ImportError as e:
    print(e)
