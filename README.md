# General SQL

Sql 生成器工具

通用格式 处理不同数据库的数据 可根据 Template(模板) 进行自定义扩展

可参考 db/Jmysql.py

已支持数据库

- mysql


## 使用示例

基本格式

```python
import GeneralSQL


# mysql 创建数据库连接
conf = {
    # 数据库名称
    'database': 'test',
    'user': 'tester',
    'passwd': '123456',
}
# 实例化 数据库对象
odb = GeneralSQL.SeniorDB('mysql')
# 设置配置
odb.set_conf(**conf)
# 链接数据库
odb.connect()

# 根据数据库对象 进行实例化 sql对象
sql = GeneralSQL.SeniorSQL(odb)

# 执行sql
odb.run(sql)

# 关闭链接
odb.close()

```

SeniorSQL 基本使用

```python
import GeneralSQL

sql = GeneralSQL.SeniorSQL(odb)

# 添加数据 sql 生成
# 添加 单一 数据
data = {
    'name': 'A1',
    'age': 12,
}
# 添加 多条 数据
# data = [
#     {'name': 'A1', 'age': 12},
#     {'name': 'A2', 'age': 13},
# ]
sql.Add(table = 'user', data = data)
# 格式化sql
sql.format_sql()
# 查看sql
print(sql.get_sql())
# >>> ["INSERT INTO config (`name`,`age`) VALUES ('A1','12')"]


# 修改数据 sql 生成
data = {
    'name': 'A1',
    'age': 12,
}
sql.Up(table = 'user', data = data)
# 设置条件
sql.set_where({
    'symbol': '=',
    'field': 'id',
    'value': 1
})
sql.formate_sql()
print(sql.get_sql())
# >>> UPDATE user SET `name` = 'A1',`age` = '12' WHERE `id` = 1


# 删除 数据
sql.Del(table = 'user')
sql.set_where({
    'symbol': '=',
    'field': 'id',
    'value': 1
})
sql.format_sql()
print(sql.get_sql())
# >>> DELETE FROM user WHERE `id` = 1


# 查询 数据
# 简单查询
sql.Sel(table = 'user')
sql.format_sql()
print(sql.get_sql())
# >>> SELECT * FROM user

# 添加条件查询
sql.Sel(table = 'user')
sql.set_where({
    'symbol': '>',
    'field': 'id',
    'value': 1
})
sql.format_sql()
print(sql.get_sql())
# >>> SELECT * FROM user WHERE `id` > 1

# 分页查询
sql.Sel(table = 'user')
sql.set_where({
    'symbol': '>',
    'field': 'id',
    'value': 1
})
sql.set_limit(row = 0, num = 2)
sql.format_sql()
print(sql.get_sql())
# >>> SELECT * FROM user WHERE `id` > 1 LIMIT 0, 2

# 分组查询
sql.Sel(table = 'user', fields = ['name', 'age'])
sql.set_group('age')
sql.format_sql()
print(sql.get_sql())
# >>> SELECT name,age FROM user GROUP BY `age`

# 排序查询
sql.Sel(table = 'user', fields = ['name', 'age'])
sql.set_group('age')
sql.set_order(**{'id': 1})
sql.format_sql()
print(sql.get_sql())
# >>> SELECT name,age FROM user GROUP BY `age` ORDER BY `id` DESC

# 连表查询
sql.Sel(table = {'user': 'u'})
sql.set_fields({
    'u__name': 'name',
    'u__age': 'age',
    'c__name': 'class_name'
})
sql.set_join({
    'keyword': 'join',
    'table': 'class',
    'table_as': 'c',
    'col_key': 'class_id',
    'col_value': 'u.id'
})
sql.format_sql()
print(sql.get_sql())
# >>> SELECT u.`name` AS `name`,u.`age` AS `age`,c.`name` AS `class_name` FROM user u JOIN class c ON c.`class_id` = u.id

```

