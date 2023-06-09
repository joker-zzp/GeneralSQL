# Mysql Maridb

## 方法详解

### *`GeneralSQL.SeniorDB`* 对象的 方法&参数

- *`set_conf(database, user, passwd, host, port) -> None`*
- *`get_conf() -> dict`*
- *`connect()`*
- *`close()`*

### *`GeneralSQL.SeniorSQL`* 对象的 方法&参数

- *`Add(table, data) -> sql`* 添加数据 table 表名 data 数据 返回 sql 对象
  - *`data_decode(data)`* 数据解码
  - *`format_sql()`* 格式化 sql 对象
- *`Del(table)` -> sql* 删除数据 返回 sql 对象
  - *`set_where(*filters)`* 设置条件 filters 过滤数据
  - *`format_sql()`* 格式化 sql 对象
- *`Up(table, data) -> sql`* 更新数据 返回 sql 对象
  - *`data_decode()`* 数据解码
  - *`set_where(*filters)`* 设置条件 filters 过滤数据
  - *`format_sql()`* 格式化 sql 对象
- *`Sel(table, fields) -> sql`* 查询数据 定义Sql类型 table 表名, fields 字段 返回 sql 对象
  - *`set_fields(*fields)`* 设置查询字段 fields 字段
  - *`set_where(*filters)`* 设置条件 filters 过滤数据
  - *`set_group(*fields)`* 设置分组 fields 字段
  - *`set_order(**fields)`* 设置排序 fields 字段
  - *`set_limit(row, num)`* 设置分页 row 行 num 数字
  - *`set_join(*join_obj)`* 设置连表对象
  - *`format_sql()`* 格式化 sql 对象
  - *`format_data(t = 'dict')`* 格式化 数据结果

## 应用实例

### 连接数据库

```python
import GeneralSQL

# mysql 配置
conf = {
    'database': "test",
    'user': 'tester',
    'passwd': '123456',
}

odb = GeneralSQL.SeniorDB('mysql')
odb.set_conf(**conf)
odb.connect()
sql = GeneralSQL.SeniorSQL(odb)
odb.run(sql)
odb.close()
```

### 添加数据

```python
import GeneralSQL
# 初始化 sql 对象
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
```

### 修改数据

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
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
```

### 删除数据

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
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
```

### 查询数据

- 简单查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
# 简单查询
sql.Sel(table = 'user')
sql.format_sql()
print(sql.get_sql())
# >>> SELECT * FROM user
```

- 条件查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
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
```

- 分页查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
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
```

- 分组查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
# 分组查询
sql.Sel(table = 'user', fields = ['name', 'age'])
sql.set_group('age')
sql.format_sql()
print(sql.get_sql())
# >>> SELECT name,age FROM user GROUP BY `age`
```

- 排序查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
# 排序查询
sql.Sel(table = 'user', fields = ['name', 'age'])
sql.set_group('age')
sql.set_order(**{'id': 1})
sql.format_sql()
print(sql.get_sql())
# >>> SELECT name,age FROM user GROUP BY `age` ORDER BY `id` DESC
```

- 连表查询

```python
import GeneralSQL
# 初始化 sql 对象
sql = GeneralSQL.SeniorSQL(odb)
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
