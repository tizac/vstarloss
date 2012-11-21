#!/usr/bin/python
#coding:utf-8

import web
import re
import time

from datetime import datetime
from web.utils import storage


from sqlalchemy import create_engine
#engine = create_engine("mysql://tizac:m1y4q5tb@localhost/dongdong?charset=utf8" , echo=False)
engine = create_engine("sqlite:///dongdong.db" , echo=False)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Table, Text
from sqlalchemy import ForeignKey
from sqlalchemy import and_, or_
from sqlalchemy.orm import relationship, backref


class Word(Base):
    __tablename__ = 'Word'

    id = Column(Integer, unique=True, primary_key=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(256), nullable=False)
    time = Column(DateTime, nullable=False)
    hide = Column(Integer, nullable=False)

    def __init__(self, args):
        self.title = args.title
        self.content = args.content
        self.author = args.author
        self.time = datetime.now()
        self.hide = 0

    def __repr__(self):
        return "<Word('%r')>" % self.id


class Article(Base):
    __tablename__ = 'Article'

    id = Column(Integer, unique=True, primary_key=True)
    title = Column(String(256), nullable=False)
    time = Column(DateTime)
    source = Column(String(256))
    content = Column(Text, nullable=False)
    catalog_id = Column(Integer, ForeignKey('Catalog.id'))
    ishtml = Column(Integer, nullable=False )
    catalog = relationship('Catalog', backref = backref('article', order_by=time))

    def __init__(self, args):
        self.update(args)

    def update(self, args):
        self.title = args.title
        if args.time:
            ttuple = time.strptime(args.time, "%Y-%m-%d")
            tdate = datetime(ttuple[0],ttuple[1],ttuple[2])
            self.time = tdate
        self.source = args.source
        self.content = args.content 
        try:
            c1 = web.ctx.orm.query(Catalog).filter_by(name = args.catalog).one()
        except:
            c1 = Catalog(args.catalog)
        self.catalog = c1 

    def __repr__(self):
        return "<Article('%r')>" % self.id

    def content_to_html(self):
        #print "%r"%self.content
        if self.ishtml==1:
            html=self.content
        else:
            strbr = re.compile(r'\r\n')
            html = strbr.sub('<br/>', self.content)
        #strspace = re.compile(r' ')
        #html = strspace.sub('&nbsp;', html)
        #html = markdown.markdown(html)
        #print html
        return html


class Catalog(Base):
    __tablename__ = 'Catalog'
    
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    weight = Column(Integer, nullable=False )
    channel = Column(Integer, nullable=False )

    def __init__(self,name):
        self.name=name

    def __repr__(self):
        return 'Catalog(%r)' % (self.name)


class Image(Base):
    __tablename__='Image'
    
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, unique=True)
    article_id = Column(Integer, ForeignKey('Article.id'))
    article = relationship('Article', backref = backref('image'))

    def __init__(self, name, article_id):
        self.name = name
        a1 = web.ctx.orm.query(Article).filter_by(id = article_id).one()
        self.article = a1

    def __repr__(self):
        return 'Image(%r, %r)' % (self.id, self.name)


class Photo(Base):
    __tablename__='Photo'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    year = Column(Integer)
    name = Column(String(256), nullable=False, unique=True)


class Vedio(Base):
    __tablename__='Vedio'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    #name = Column(String(256), nullable=False, unique=True)
    title = Column(String(256), nullable=False, unique=True)
    url = Column(String(512), nullable=False, unique=True)
    catalog_id = Column(Integer, ForeignKey('Catalog.id'))
    catalog = relationship('Catalog', backref = backref('vedio', order_by=title))



    def __init__(self, args):
        self.update(args)

    def update(self, args):
        self.title= args.title
        self.url = args.url
        try:
            c1 = web.ctx.orm.query(Catalog).filter_by(name = args.catalog).one()
        except:
            c1 = Catalog(args.catalog)
        self.catalog = c1 



#---------------------------------------------------------------------

metadata = Base.metadata

if __name__ == "__main__":
    metadata.create_all(engine)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
