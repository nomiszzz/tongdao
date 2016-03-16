#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import contextlib
import datetime
from settings import dbconn as conn
from settings import config

logger = logging.getLogger('orm')
logger.setLevel(config.ORM_LOGGER_LEVEL)


class FieldException(Exception):
    pass


class FieldTypeException(Exception):
    pass


class FieldType(object):
    VARCHAR = 11
    CHAR = 12

    TEXT = 21
    LONGTEXT = 22

    TINYINT = 31
    INT = 32
    BIGINT = 33

    FLOAT = 41
    DECIMAL = 42

    DATETIME = 51
    TIMESTAMP = 52

    BOOLEAN = 61


    @classmethod
    def get_map(cls):
        map_dict = {value: key for key, value in cls.__dict__.items() if not key.startswith('__')}
        map_dict.pop('map')
        return map_dict

    @classmethod
    def get_string_type(cls):
        return {value: key for key, value in cls.__dict__.items() if 10 < value < 20}

    @classmethod
    def get_text_type(cls):
        return {value: key for key, value in cls.__dict__.items() if 20 < value < 30}

    @classmethod
    def get_integer_type(cls):
        return {value: key for key, value in cls.__dict__.items() if 30 < value < 40}

    @classmethod
    def get_float_type(cls):
        return {value: key for key, value in cls.__dict__.items() if 40 < value < 50}

    @classmethod
    def get_time_type(cls):
        return {value: key for key, value in cls.__dict__.items() if 50 < value < 60}

    @classmethod
    def get_boolean_type(cls):
        return {FieldType.BOOLEAN: 'TINYINT(1)'}


class Field(object):
    _count = 0

    def __init__(self, name=None, length=None, fieldtype='', primary_key=False, default=None, nullable=True,
                 updateable=True, insertable=True, auto_increment=False, **kwargs):
        self.name = name
        self.length = length
        self._default = default
        self._onupdate = kwargs.get('onupdate', None)
        self.fieldtype = fieldtype
        self.primary_key = primary_key
        self.nullable = nullable
        self.updateable = updateable
        self.insertable = insertable
        self.auto_increment = auto_increment

        self._order = Field._count
        Field._count += 1


    @property
    def default(self):
        d = self._default
        return d() if callable(d) else d

    @property
    def onupdate(self):
        d = self._onupdate
        return d() if callable(d) else d


    def __repr__(self):
        s = ["<{}:{}, {}, default({}), ".format(self.__class__.__name__, self.name, self.fieldtype, self._default)]
        self.nullable and s.append('N')
        self.updateable and s.append('U')
        self.insertable and s.append('I')
        s.append('>')
        return ''.join(s)


class FieldTypeMixin(object):
    def __init__(self):
        self.length = None
        self.fieldtype = None


    def valid_length(self):
        if not (self.length and isinstance(self.length, int)):
            raise FieldTypeException('Field must define a right length attribute')

    def valid_type(self, rtype):
        if rtype == 'string':
            field_type = FieldType.get_string_type().get(self.fieldtype)
        elif rtype == 'text':
            field_type = FieldType.get_text_type().get(self.fieldtype)
        elif rtype == 'integer':
            field_type = FieldType.get_integer_type().get(self.fieldtype)
        elif rtype == 'float':
            field_type = FieldType.get_float_type().get(self.fieldtype)
        elif rtype == 'time':
            field_type = FieldType.get_time_type().get(self.fieldtype)
        elif rtype == 'boolean':
            field_type = FieldType.get_boolean_type().get(self.fieldtype)
        else:
            field_type = ''
        if not field_type:
            raise FieldTypeException('{} Field type error, check the FieldType class'.format(rtype.capitalize()))
        return field_type


class String(Field, FieldTypeMixin):
    def __init__(self, length=None, fieldtype=FieldType.VARCHAR, default=None, **kwargs):
        self.length = length
        self.fieldtype = fieldtype

        self.valid_length()
        string_type = self.valid_type('string')

        kwargs['fieldtype'] = "{}({})".format(string_type, self.length)
        kwargs['default'] = default
        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(String, self).__init__(**kwargs)


class Text(Field, FieldTypeMixin):
    def __init__(self, fieldtype=FieldType.TEXT, default=None, **kwargs):
        self.fieldtype = fieldtype
        string_type = self.valid_type('text')

        kwargs['fieldtype'] = "{}".format(string_type)
        kwargs['default'] = default

        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(Text, self).__init__(**kwargs)


class Integer(Field, FieldTypeMixin):
    def __init__(self, length=None, fieldtype=FieldType.INT, default=None, auto_increment=False, primary_key=False,
                 **kwargs):
        self.length = length
        self.fieldtype = fieldtype
        self.valid_length()

        integer_type = self.valid_type('integer')
        kwargs['fieldtype'] = "{}({})".format(integer_type, self.length)
        kwargs['auto_increment'] = auto_increment
        kwargs['default'] = default
        kwargs['primary_key'] = primary_key

        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(Integer, self).__init__(**kwargs)


class Float(Field, FieldTypeMixin):
    def __init__(self, length=None, fieldtype=FieldType.FLOAT, default=None, **kwargs):
        self.length = length
        self.valid_length()

        self.fieldtype = fieldtype
        integer_type = self.valid_type('float')

        kwargs['fieldtype'] = "{}({})".format(integer_type, self.length)
        kwargs['default'] = default

        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(Float, self).__init__(**kwargs)


class Time(Field, FieldTypeMixin):
    def __init__(self, fieldtype=FieldType.DATETIME, default=None, onupdate=None, **kwargs):
        self.fieldtype = fieldtype
        integer_type = self.valid_type('time')

        kwargs['fieldtype'] = "{}".format(integer_type)
        kwargs['onupdate'] = onupdate
        kwargs['default'] = default or datetime.datetime.now()
        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(Time, self).__init__(**kwargs)


class Boolean(Field, FieldTypeMixin):
    def __init__(self, fieldtype=FieldType.BOOLEAN, **kwargs):
        self.fieldtype = fieldtype
        integer_type = self.valid_type('boolean')

        kwargs['fieldtype'] = "{}".format(integer_type)
        kwargs['default'] = kwargs.get('default', 0)
        logger.info('{} Field kwargs {}'.format(self.__class__.__name__, kwargs))
        super(Boolean, self).__init__(**kwargs)


def create_table_sql(table_name, mappings):
    pk = None
    sql = ["CREATE TABLE `{table_name}` (".format(table_name=table_name)]

    for field in sorted(mappings.values(), lambda x, y: cmp(x._order, y._order)):
        if not hasattr(field, 'fieldtype'):
            raise StandardError('No fieldtype in field "{0}".'.format(field.name))

        name = field.name
        fieldtype = field.fieldtype
        nullable = field.nullable
        default = field.default

        if field.primary_key:
            pk = field.name
            sql.append("    `{name}` {fieldtype} AUTO_INCREMENT, ".format(name=name, fieldtype=fieldtype))
        else:
            if field.default is not None:
                if isinstance(field, String) or isinstance(field, Text):
                    default = "'{}'".format(field.default)
                elif isinstance(field, Time):
                    default = "CURRENT_TIMESTAMP"
                    if field.onupdate:
                        default = "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                sql.append(nullable and "    `{}` {} DEFAULT {}, ".format(
                    name, fieldtype, default) or "    `{}` {} DEFAULT {}, ".format(
                    name, fieldtype, default))
            else:
                sql.append(nullable and "    `{}` {},".format(name, fieldtype) or "    `{}` {} NOT NULL,".format(
                    name, fieldtype))
    sql.append("    PRIMARY KEY(`{}`)".format(pk))
    sql.append(") DEFAULT CHARSET=utf8;")
    return '\n'.join(sql)


class ModelMetaClass(type):
    def __new__(cls, cname, bases, attrs):

        if cname == 'Model':
            return super(ModelMetaClass, cls).__new__(cls, cname, bases, attrs)

        mappings = dict()
        primary_key = False
        for attr_name, attr_value_field in attrs.iteritems():
            if isinstance(attr_value_field, Field):
                if not attr_value_field.name:
                    attr_value_field.name = attr_name
                logger.info('Found mapping: {} => {}'.format(attr_name, attr_value_field))
                if attr_value_field.primary_key:
                    if primary_key:
                        raise TypeError('Cannot define more than 1 primary key in class: {0}'.format(cname))
                    if attr_value_field.nullable:
                        logger.warning('NOTE: change primary key to non-nullable.')
                        attr_value_field.nullable = False
                    if attr_value_field.updateable:
                        logger.warning('NOTE: change primary key to non-updateable.')
                        attr_value_field.updateable = False
                    if not attr_value_field.auto_increment:
                        logger.warning('NOTE: the primary key auto_increment must True')
                        attr_value_field.auto_increment = True
                    primary_key = attr_value_field
                mappings[attr_name] = attr_value_field

        if not primary_key:
            raise TypeError('Primary key not defined in class: {0}'.format(cname))

        for attr_name in mappings.iterkeys():
            attrs.pop(attr_name)
        if not '__table__' in attrs:
            attrs['__table__'] = cname.lower()

        attrs['__mappings__'] = mappings
        attrs['__primary_key__'] = primary_key
        attrs['__create_table_sql__'] = lambda cls: create_table_sql(attrs['__table__'], mappings)
        return super(ModelMetaClass, cls).__new__(cls, cname, bases, attrs)


class Model(dict):
    __metaclass__ = ModelMetaClass

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            if item == 'id':
                return
            raise AttributeError("'Dict' object has no attribute '{}'".format(item))

    def __setattr__(self, key, value):
        self[key] = value

    @staticmethod
    def db():
        return conn._db

    @staticmethod
    def _where(**kwargs):
        wheres = []
        args = []
        for k, v in kwargs.iteritems():
            wheres.append("{}=%s ".format(k))
            args.append(v)
        where = 'AND '.join(wheres)
        return where, args

    @classmethod
    def show_fields(cls):
        return [field for field in cls.__mappings__]

    @classmethod
    def count(cls, **kwargs):
        where, args = cls._where(**kwargs)
        if where:
            query = "SELECT COUNT(*) FROM `{table}` WHERE {where}".format(table=cls.__table__, where=where)
        else:
            query = "SELECT COUNT(*) FROM `{table}`".format(table=cls.__table__)
        logger.info('The SQL is {}'.format(query))
        count = conn.query(query, *args)
        if count:
            return count[0].get('COUNT(*)')
        return 0

    @classmethod
    def getone(cls, pk):
        query = "SELECT * FROM `{table}` WHERE id=%s LIMIT 1".format(table=cls.__table__)
        logger.info('The SQL is {0}'.format(query))
        result = conn.get(query, pk)
        return cls(**result) if result else None

    @classmethod
    def findone(cls, **kwargs):
        where = " AND  ".join(["`{0}`=%s".format(k) for k in kwargs])
        query = "SELECT * FROM `{table}`  WHERE {where} LIMIT 1".format(table=cls.__table__, where=where)
        logger.info('the SQL is {0}'.format(query))
        d = conn.get(query, *kwargs.values())
        return cls(**d) if d else None

    @classmethod
    def findall(cls, **kwargs):
        where, args = cls._where(**kwargs)
        if where:
            query = "SELECT * FROM `{table}` WHERE {where}".format(table=cls.__table__, where=where)
        else:
            query = "SELECT * FROM `{table}`".format(table=cls.__table__)
        logger.info('the SQL is {0}'.format(query))
        result = conn.query(query, *args)
        return [cls(**d) for d in result if result]

    @classmethod
    def filter(cls, orderby='', rows=0, offset=10, **kwargs):
        """
        复杂的查询，返回包装后的model对象列表。
        :param orderby: orderby排序字典
        :param rows: limit参数
        :param offset:  limit参数，偏移量
        :param kwargs: 查询where条件

        >>> users = User.filter(orderby={"password": "DESC"}, rows=0, offset=2, email='r@g.com')
        """
        where, args = cls._where(**kwargs)
        if orderby:
            sorts = []
            for field, sort in orderby.iteritems():
                sorts.append("{} {} ".format(field, sort.upper()))
            orderby = "ORDER BY {}".format(', '.join(sorts))

        if where:
            query = ("SELECT * FROM `{table}` "
                     "WHERE {where} "
                     "{orderby} "
                     "LIMIT {rows}, {offset}".format(table=cls.__table__, where=where, orderby=orderby,
                                                     rows=rows, offset=offset))

        else:
            query = ("SELECT * FROM `{table}` "
                     "{orderby} "
                     "LIMIT {rows}, {offset}".format(table=cls.__table__, where=where, orderby=orderby,
                                                     rows=rows, offset=offset))

        logger.info('the SQL is {0}'.format(query))
        result = conn.query(query, *args)
        return [cls(**d) for d in result if result]

    @classmethod
    def remove(cls, **kwargs):
        where, args = cls._where(**kwargs)
        query = ("DELETE FROM `{table}` WHERE {where}".format(table=cls.__table__, where=where))
        logger.info('The SQL is {0}'.format(query))
        rowcount = conn.update(query, *args)
        return rowcount

    @classmethod
    def raw_query(cls, sql, *args):
        """执行原生的sql语句，分包装的sql查询结果，适用于联合查询"""
        result = conn.query(sql, *args)
        return result

    @classmethod
    def raw_get(cls, sql, *args):
        """执行原生的sql语句，分包装的sql查询结果，适用于联合查询, 仅返回一条数据"""
        result = conn.get(sql, *args)
        return result

    @classmethod
    def raw_select(cls, sql, *args):
        """执行原生的select sql语句，返回models包装之后的对象列表"""
        result = conn.query(sql, *args)
        return [cls(**d) for d in result if result]

    @classmethod
    def raw_update(cls, sql, *args):
        rowcount = conn.update(sql, *args)
        return rowcount

    @classmethod
    def raw_delete(cls, sql, *args):
        """ 执行delete删除sql语句
        >>> sql = "DELETE FROM `{table}` WHERE username=%s".format(table=User.__table__)
        >>> row = User.raw_delete(sql, 'rsj217')
        """
        rowcount = conn.update(sql, *args)
        return rowcount

    @classmethod
    def raw_execute(cls, sql, *args):
        lastrowid = conn.execute(sql, *args)
        return lastrowid

    @classmethod
    def raw_insert(cls, sql, *args):
        """
        执行插入语句
        :param sql: insert into 语句
        :param args: 插入的参数
        :return: 插入成功之后记录的pk

        >>> sql = "INSERT INTO `{table}` (username) values (%s)".format(table=User.__table__)
        >>> row = User.raw_insert(sql, 'admin')
        """
        lastrowid = conn.execute(sql, *args)
        return lastrowid

    @classmethod
    @contextlib.contextmanager
    def transition(cls):
        """
        >>> with User.transition():
        >>> user = User(username='rsj217')
        >>> user.insert()
        >>> raise
        """

        conn._db.begin()
        logger.info("Start Transition")
        try:
            yield
            conn._db.commit()
            logger.info("Commit")
        except:
            conn._db.rollback()
            logger.warning("Rollback")

    @classmethod
    def create(cls):
        query = cls.__dict__['__create_table_sql'](cls)
        if not cls.is_table_exist():
            conn.execute(query)

    @classmethod
    def is_table_exist(cls, dbname=config.MYSQLDB['db']):
        table = cls.__dict__['__table__']

        query = "SELECT table_name FROM information_schema.TABLES WHERE table_name='{}' AND table_schema='{}'".format(
            table, dbname)
        row = conn.query(query)
        return True if row else False


    @classmethod
    def drop(cls):
        query = "DROP TABLE IF EXISTS {}".format(cls.__table__)
        conn.update(query)
        logger.info('The SQL is {0}'.format(query))
        logger.warning("Drop table {}".format(cls.__table__))

    def insert(self):
        """插入对象
        :return: 插入成功之后记录的pk

        >>> user = User(username='rsj217')
        >>> user.insert()
        """

        params = dict()
        for k, v in self.__mappings__.iteritems():
            if v.insertable:
                if not hasattr(self, k):
                    setattr(self, k, v.default)
                params[v.name] = getattr(self, k)
        cols, args = zip(*params.iteritems())
        query = "INSERT INTO `{table}` ({fields}) values ({values})".format(table=self.__table__, fields=','.join(
            ['`%s`' % col for col in cols]), values=','.join(['%s' for i in range(len(cols))]))
        logger.info('The SQL is {0}'.format(query))
        lastrowid = conn.execute(query, *args)
        return lastrowid

    def update(self):
        """
        model 实例对象的更新方法，与delete一样，只能用于从数据库查询获取的model对象。直接使用model初始化的对象并不会执行该方法。
        >>> user = User.findone(password='111')
        >>> user.username = 'admin'
        >>> user.update()
        """

        L = []
        args = []
        pk = self.__primary_key__.name
        for k, v in self.__mappings__.iteritems():
            if v.name != pk:
                if v.updateable:
                    if not v.onupdate:
                        if hasattr(self, k):
                            arg = getattr(self, k)
                        else:
                            arg = v.default
                            setattr(self, k, arg)
                        L.append("`{}`=%s".format(k))
                        args.append(arg)
                else:
                    raise StandardError("Field {} cannot update ".format(k))

        args.append(getattr(self, pk))
        query = "UPDATE `{table}` SET {fields_values} WHERE {pk_name}=%s".format(table=self.__table__,
                                                                                 fields_values=','.join(L),
                                                                                 pk_name=pk)
        logger.info('The SQL is {0}, the args is {1}'.format(query, args))
        rowcount = conn.update(query, *args)
        return rowcount

    def delete(self):
        """
        删除方法，model的实例对象才能调用，并且是id有值的，通过models直接创建的对象，并不是数据库的实体，故没有该方法

        >>> user = User.findone(username='admin')
        >>> row = user.delete()
        """
        pk = self.__primary_key__.name
        if hasattr(self, pk):
            args = getattr(self, pk)
            query = "DELETE FROM `{table}` WHERE {pk_name}=%s".format(table=self.__table__, pk_name=pk)
            logger.info('The SQL is {0}'.format(query))
            rowcount = conn.update(query, args)
            logger.warning("Delete table {} where pk {} rowcount {}".format(self.__table__, pk, rowcount))
            return rowcount
        else:
            raise StandardError("Current object cannot delete by '{}'".format(pk))


if __name__ == '__main__':
    import torndb

    conn = torndb.Connection(host='localhost', user='root', database='tornapro')

    class User(Model):

        __table__ = 'user'

        id = Integer(length=10, primary_key=True)
        username = String(length=10, nullable=False)
        email = String(length=40)
        password = String(length=60)
        create_at = Time(default=datetime.datetime.now)
        update_at = Time(onupdate=True)


    print User.__dict__['__create_table_sql__'](User)

    def raw_transition():
        cursor = conn._cursor()
        status = True
        cursor.execute("BEGIN")
        try:
            cursor.execute("INSERT INTO `user` (username) values ('rsj217') ")
            cursor.execute("COMMIT")
        except:
            cursor.execute("ROLLBACK")
            status = False

        cursor.close()
        print status

    def model_transition():
        conn._db.begin()
        try:
            user = User(username='rsj217')
            user.insert()
            conn._db.commit()
        except:
            conn._db.rollback()

    def obj_transition():
        with User.transition():
            user = User(username='admin')
            user.insert()
            raise