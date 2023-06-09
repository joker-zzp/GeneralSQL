# General SQL

Sql 生成器工具

通用格式 处理不同数据库的数据 可根据 Template(模板) 进行自定义扩展

可参考 db/Jmysql.py

已支持数据库

- mysql 安装 `pip install mysql-connector`

## 使用示例

- [mysql, mariadb](https://github.com/joker-zzp/GeneralSQL/blob/master/doc/mysql.md)

## 各种方法详细使用设计

*`GeneralSQL`* 中目前有2种主要对象

- *`SeniorDB`* 数据库对象
    - *`set_conf()`* 设置数据库对象的配置(连接配置)
    - *`get_conf()`* 获取配置信息
    - *`connect()`* 数据库连接
    - *`close()`* 关闭连接
- *`SeniorSQL`* sql 对象
    - *`Add(*args, **kwargs) -> sql`* 添加数据方法 返回 sql 对象
    - *`Del(*args, **kwargs) -> sql`* 删除数据方法 返回 sql 对象
    - *`Up(*args, **kwargs) -> sql`* 更新数据方法 返回 sql 对象
    - *`Sel(*args, **kwargs) -> sql`* 查询数据方法 返回 sql 对象
- sql 对象方法
    - *`set_join(*args, **kwargs)`* 设置连表查询
    - *`set_where(*args, **kwargs)`* 设置条件
    - *`set_group(*args, **kwargs)`* 设置分组
    - *`set_order(*args, **kwargs)`* 设置排序
    - *`set_limit(*args, **kwargs)`* 设置分页
    - *`data_decode(*args, **kwargs)`* 数据解码
    - *`format_sql(*args, **kwargs)`* 格式化数据
    - *`format_data(*args, **kwargs)`* 格式化数据
