# General SQL
General SQL generating tool from simple to complex.

## 简单介绍

这个工具可以帮助你简单的完成稍微复杂定制化的 SQL ，如果你对 SQL 不太熟练也可以尝试这个工具来帮你完成较为复杂的 SQL 语句。
工具的详细介绍可以查看下使用实例，这个帮助你快速上手，欢迎使用这个工具希望对你的工作有所帮助。

ps: 在学习 SQL 的人也可以轻松的使用这个工具，来帮助你快速学习 SQL 。

## 示例

### 基本使用

如何导入库 执行指定 sql

```python
import GeneralSQL

db_info = {
    'database': 'sql_test',
    'user': 'test',
    'password': '000000',
    'host': 'localhost',
    'port': 3306
}
# 实例化一个 SeniorSQL 对象
t = GeneralSQL.SeniorSQL()
# 设置连接数据库
t.set_db_info(**db_info)
# 设置 sql: show tables;
t.set_sql('show tables')
# 执行 sql 获取结果, get_date() 方法会返回元组格式数据原型
t.get_date()
# 将查询结果格式化成字典赋值
res = t.get_format_data()
# 断开数据库连接
t.close()
```

### 简单操作

#### 添加数据

mysql 示例sql

```mariadb
INSERT INTO class(`class_name`,`class_grade`,`class_type`) VALUES ("1班","初一","中学"),("2班","初一","中学"),("3班","初一","中学");
```

python 代码

```python
# 基本操作
t = GeneralSQL.SeniorSQL()
t.set_db_info(**db_info)
# 创造数据
col = ['class_name', 'class_grade', 'class_type']
add_data = [
    {'class_name': '1班', 'class_grade': '初一', 'class_type': '中学'},
    {'class_name': '2班', 'class_grade': '初一', 'class_type': '中学'},
    {'class_name': '3班', 'class_grade': '初一', 'class_type': '中学'}
]
# 设置格式化 sql
t.Add('class', col, add_data)
# 格式化sql
t.get_func_sql('add')
# 查看 insert sql 数据列表
# print(t.get_sql_list())
# >>> ['INSERT INTO class(`class_name`,`class_grade`,`class_type`) VALUES ("1班","初一","中学"),("2班","初一","中学"),("3班","初一","中学")']

# 执行 sql 获取执行结果
t.get_insert_data()
# 提交数据
t.commit()
# 回滚 t.rollback()
# 断开连接
t.close()
```

#### 修改数据

mysql 示例sql

```mariadb
UPDATE class SET class_grade="初二";
```

python 代码

```python
# 基本操作
t = GeneralSQL.SeniorSQL()
t.set_db_info(**db_info)
# 修改数据
up_data = {
    'class_grade': '初二'
}
# 设置更新表数据
t.Up('class', **up_data)
# 生成更新方法sql
t.get_func_sql('up')
# 查看 sql
print(t.get_sql())
# 执行 sql
t.get_data()
# 获取更新结果
res = t.get_format_data()
# 提交数据
t.commit()
# 断开连接
t.close()
```

#### 删除数据

mysql 示例sql

```mariadb
DELETE FROM class
```

python 代码

```python
# 基本操作
t = GeneralSQL.SeniorSQL()
t.set_db_info(**db_info)
# 设置删除表
t.Del('class')
# 生成删除方法sql
t.get_func_sql('del')
# 查看 sql
print(t.get_sql())
# 执行 sql
t.get_data()
# 获取更新结果
res = t.get_format_data()
# 提交数据
t.commit()
# 断开连接
t.close()
```

#### 查询数据

mysql 示例sql

```mariadb
SELECT class_id,class_name,class_grade,class_type,class_create_time FROM class
```

python 代码

```python
# 基本操作
t = GeneralSQL.SeniorSQL()
t.set_db_info(**db_info)
# 设置查询字段
col = ['class_id', 'class_name', 'class_grade', 'class_type', 'class_create_time']
# 设置查询表
t.Sel('class', *col)
# 生成查询方法sql
t.get_func_sql('sel')
# 查看 sql
print(t.get_sql())
# 执行 sql
t.get_data()
# 获取更新结果
res = t.get_format_data()
# 断开连接
t.close()
```

### 进阶操作

当你在已经了解了关于 General SQL 的简单操作后，是不是感觉很容易。
简单操作主要是面向对于刚刚了解 sql 的朋友，对于接下讲解内容是关于 查询 的。如果你准备好了就开始吧～

未完待续...