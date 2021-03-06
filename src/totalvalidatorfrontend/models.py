# -*- encoding: utf-8 -*-
from pyramid.security import Allow
from pyramid.security import DENY_ALL
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Authenticated
from pyramid.security import Everyone

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class RootFactory(object):
    __acl__ = [
        (Allow, Authenticated, ALL_PERMISSIONS),
        (Allow, Everyone, 'public'),
        DENY_ALL
    ]

    def __init__(self, request):
        pass


class ValidationSessionModel(Base):
    """This model represents a validation session.
    """
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    code = Column(String(100), unique=True)
    date = Column(DateTime, nullable=True)
    # max number of pages to validate (0 == nolimit)
    limit = Column(Integer(3), default=0)
    # 0 nothing done
    # 1 scraping
    # 2 checking html/css etc.
    # 3 check done
    status = Column(Integer(1), default=0)


def create_or_clean_tables(session_code):
    """Clean up all tables related to a specific
    validation session.

    :param session_code: validation session uuid
    :type session_code: string
    """
    models = [
        get_urls_model(session_code),
        get_accessibility_validator_model(session_code),
        get_markup_validator_model(session_code),
        get_css_validator_model(session_code)
    ]
    for m in models:
        DBSession.query(m).delete()
        DBSession.flush()


def get_urls_model(session_code):
    """Create urls table for a specific validation session
    and map it to a SqlAlchemy model class

    :param session_code: validation session uuid
    :type session_code: string
    """
    name = '{}_urls'.format(session_code)
    _table = Table(
        name,
        Base.metadata,
        Column("id",  Integer, primary_key=True),
        Column("url",  String(255)),
        Column('date', DateTime),
        Column('warning_markup', Integer(3), default=0),
        Column('error_markup', Integer(3), default=0),
        Column('warning_accessibility', Integer(3), default=0),
        Column('error_accessibility', Integer(3), default=0),
        keep_existing=True
    )
    _table.create(checkfirst=True)
    attr_dict = {
        '__tablename__': name,
        '__table_args__': {'autoload': True},
    }

    UrlsModel = type('URLSModel', (Base, ), attr_dict)
    return UrlsModel


def get_markup_validator_model(session_code):
    """Create markup validation table for a specific validation session
    and map it to a SqlAlchemy model class

    :param session_code: validation session uuid
    :type session_code: string
    """

    name = '{}_markup'.format(session_code)
    _table = Table(
        name,
        Base.metadata,
        Column("id",  Integer, primary_key=True),
        Column("url",  String(255)),
        Column('type', String(17)),
        Column('line', Integer(10)),
        Column('column', Integer(10)),
        Column("error", Text),
        Column('errorhash', String(100)),
        Column('messageid', String(50)),
        Column("detail", Text),
        Column("source", Text),
        keep_existing=True
    )
    _table.create(checkfirst=True)
    attr_dict = {
        '__tablename__': name,
        '__table_args__': {'autoload': True},
    }

    MarkupModel = type('MarkupModel', (Base, ), attr_dict)
    return MarkupModel


def get_accessibility_validator_model(session_code):
    """Create accessibility validation table for a specific validation session
    and map it to a SqlAlchemy model class

    :param session_code: validation session uuid
    :type session_code: string
    """
    name = '{}_accessibility'.format(session_code)
    _table = Table(
        name,
        Base.metadata,
        Column("id",  Integer, primary_key=True),
        Column("url",  String(255)),
        Column("urlhash",  String(100)),
        Column('type', String(17)),
        Column('line', Integer(10)),
        Column('column', Integer(10)),
        Column("error", Text),
        Column("errorhash", String(100)),
        Column("source", Text),
        Column("repair", Text),
        keep_existing=True
    )

    _table.create(checkfirst=True)
    attr_dict = {
        '__tablename__': name,
        '__table_args__': {'autoload': True},
    }

    AccessibilityModel = type('AccessibilityModel', (Base, ), attr_dict)
    return AccessibilityModel


def get_css_validator_model(session_code):
    """Create CSS validation table for a specific validation session
    and map it to a SqlAlchemy model class

    :param session_code: validation session uuid
    :type session_code: string
    """
    name = '{}_css'.format(session_code)
    _table = Table(
        name,
        Base.metadata,
        Column("id",  Integer, primary_key=True),
        Column('date', DateTime),
        Column("url",  String(255)),
        Column("urlhash",  String(100)),
        Column("type",  String(17)),
        Column('errortype', String(100)),
        Column("line",  Integer(4)),
        Column("error",  Text),
        Column("errorhash",  String(100)),
        Column("source",  Text),
        Column("context",  Text),
        keep_existing=True
    )

    _table.create(checkfirst=True)
    attr_dict = {
        '__tablename__': name,
        '__table_args__': {'autoload': True},
    }

    CSSModel = type('CSSModel', (Base, ), attr_dict)
    return CSSModel
