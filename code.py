#!/usr/bin/python
#coding:utf-8

import web

#for import view and other local module
if __name__!='__main__':
	import os
	import sys
	abspath = os.path.dirname(__file__)
	sys.path.append(abspath)
	os.chdir(abspath)

import sys
if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

from view import *
from sqlalchemy.orm import scoped_session, sessionmaker

def load_sqlalchemy(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()


#--- Control settings ----
urls = (
    '/',    'index',
    '/login',   'login',
    '/logout', 'logout',
    '/events',  'events',
    '/event/(\d+)',  'event',
    '/articles',    'articles',
    '/articles/catalog/(\d+)', 'catalog',
    '/articles/catalog/create/(\d+)',    'articles_create',
    '/article/(\d+)', 'article_view',
    '/article/edit/(\d+)',    'article_edit',
    '/article/image/upload/(\d+)',  'article_image_upload',
    '/image/delete/(\d+)', 'image_delete',
    '/photos',  'photos',
    '/photos/year/(\d+)',  'photos_year',
    '/photo/(\d+)/(\d+)','photo_view',
    '/memories', 'memories',
    '/words',   'words',
    '/words/create',    'words_create',
    '/word/delete/(\d+)', 'word_delete',
    '/word/show/(\d+)', 'word_show',
    '/word/hide/(\d+)', 'word_hide',
    '/vedios',  'vedios',
    '/vedio/(\d+)', 'vedio_view',
    '/vedio/create', 'vedio_create',
    '/vedio/edit/(\d+)',    'vedio_edit',
    '/activity/goldencampass',    'activity',
    )


app = web.application(urls, globals())
app.add_processor(load_sqlalchemy)


#web.config.debug = False

if __name__!='__main__':
    session = web.session.Session(app, web.session.DiskStore(os.path.join(abspath,'sessions')),initializer={'isAdmin':0})
else:
    session = web.session.Session(app, web.session.DiskStore('sessions'),initializer={'isAdmin':0})

def session_hook():
    web.ctx.session = session
    web.template.Template.globals['session'] = session


if __name__ == "__main__":
    app.add_processor(web.loadhook(session_hook))
    app.run()
else:
    app.add_processor(web.loadhook(session_hook))
    application=app.wsgifunc()



