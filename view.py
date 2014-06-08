#!/usr/bin/python
#coding:utf-8

import os
import web
import hashlib

from model import *
from config import STATIC_PATH, PASSWD, IMG_SERVER


render = web.template.render('templates', base='base')


class login:
    def GET(self):
        return render.login()

    def POST(self):
        i = web.input(username=None, password=None)
        if i.username and i.password:
            key = hashlib.sha224(i.username+i.password).hexdigest()
            if key == PASSWD:
                web.ctx.session.isAdmin = 1
                return render.login()
        raise web.seeother('/')


def login_required(func):
    def Function(*args):
        if web.ctx.session.isAdmin == 0:
            return "Pemissions denied"
        else:
            return func(*args)
    return Function


class logout:
    @login_required
    def GET(self):
        web.ctx.session.isAdmin = 0
        raise web.seeother('/')


class index:
    def GET(self):
        return render.index()


class events:
    def GET(self):
        raise web.seeother('/event/350')


class event:
    def GET(self, id):
        article = web.ctx.orm.query(Article).filter_by(id=id).one()
        articles = web.ctx.orm.query(Article).filter(Article.catalog_id == 0).all()
        return render.event(articles, article)


class photos:
    def GET(self):
        return render.photos(IMG_SERVER)


class photos_year:
    def GET(self, year):
        photos = os.listdir(STATIC_PATH + '/photo/' + year)
        photos.sort()
        return render.photos_year(IMG_SERVER, year, photos)


class photo_view:
    def GET(self, year, idx):
        year = str(year)
        idx = int(idx)
        photos = os.listdir(STATIC_PATH + '/photo/' + year)
        photos.sort()
        total = len(photos)
        if idx >= total:
            raise web.seeother('/photo/%s/%s' % (year, idx-1))
        filename = photos[idx]
        return render.photo_view(IMG_SERVER, year, filename, total, idx)


class words:
    def GET(self):
        if web.ctx.session.isAdmin == 0:
            words = web.ctx.orm.query(Word).filter_by(hide=0).order_by(Word.time.desc()).all()
        else:
            words = web.ctx.orm.query(Word).order_by(Word.time.desc()).all()
        return render.words(words)


class words_create:
    def GET(self):
        return render.words_create()

    def POST(self):
        d = web.input()
        w1 = Word(d)
        web.ctx.orm.add(w1)
        raise web.seeother('/words')


class word_delete:
    @login_required
    def GET(self, id):
        w1 = web.ctx.orm.query(Word).filter_by(id=id).one()
        web.ctx.orm.delete(w1)
        raise web.seeother('/words')


class word_hide:
    @login_required
    def GET(self, id):
        w1 = web.ctx.orm.query(Word).filter_by(id=id).one()
        w1.hide = 1
        web.ctx.orm.add(w1)
        raise web.seeother('/words')


class word_show:
    @login_required
    def GET(self, id):
        w1 = web.ctx.orm.query(Word).filter_by(id=id).one()
        w1.hide = 0
        web.ctx.orm.add(w1)
        raise web.seeother('/words')


class articles:
    def GET(self):
        web.seeother('/articles/catalog/4')


class catalog:
    def GET(self, id):
        catalog = web.ctx.orm.query(Catalog).filter_by(id=id).one()
        catalogs = web.ctx.orm.query(Catalog).filter_by(channel=catalog.channel).order_by(Catalog.weight).all()
        articles = catalog.article
        return render.catalog(catalogs, catalog, articles)


class articles_create:
    @login_required
    def GET(self, catalog_id):
        catalog = web.ctx.orm.query(Catalog).filter_by(id=catalog_id).one()
        catalogs = web.ctx.orm.query(Catalog).all()
        return render.articles_create(catalog, catalogs)

    @login_required
    def POST(self, catalog_id):
        d = web.input()
        a1 = Article(d)
        web.ctx.orm.add(a1)
        raise web.seeother('/articles/catalog/%s' % catalog_id)


class article_view:
    def GET(self, id):
        article = web.ctx.orm.query(Article).filter_by(id=id).one()
        catalog = article.catalog
        catalogs = web.ctx.orm.query(Catalog).filter(Catalog.channel == catalog.channel).order_by(Catalog.weight).all()
        return render.article_view(catalogs, catalog, article)


class article_edit:
    @login_required
    def GET(self, id):
        article = web.ctx.orm.query(Article).filter_by(id=id).one()
        catalog = web.ctx.orm.query(Catalog).all()
        return render.article_edit(article, catalog)

    @login_required
    def POST(self, id):
        d = web.input()
        if d.submit == u"修改文章":
            article = web.ctx.orm.query(Article).filter_by(id=id).one()
            article.update(d)
            web.ctx.orm.add(article)
            catalog = article.catalog
            web.ctx.orm.commit()
            raise web.seeother('/articles/catalog/%s' % catalog.id)
        if d.submit == u"删除文章":
            article = web.ctx.orm.query(Article).filter_by(id=id).one()
            catalog = article.catalog
            web.ctx.orm.delete(article)
            raise web.seeother('/articles/catalog/%s' % catalog.id)


class article_image_upload:
    @login_required
    def GET(self, id):
        article = web.ctx.orm.query(Article).filter_by(id=id).one()
        return render.article_image_upload(article)

    @login_required
    def POST(self, id):
        x = web.input(myfile={})
        filedir = STATIC_PATH + '/img'
        if 'myfile' in x:
            # upload file
            filepath = x.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1]
            filename = unicode(filename, 'utf-8')
            filename = id + '_' + filename
            fout = open(filedir + '/' + filename, 'w')
            fout.write(x.myfile.file.read())
            fout.close()
            # save filename
            img = Image(filename, id)
            web.ctx.orm.add(img)
        raise web.seeother('/article/edit/%s' % id)


class image_delete:
    @login_required
    def POST(self, id):
        img1 = web.ctx.orm.query(Image).filter_by(id=id).one()
        os.remove(STATIC_PATH + '/img/' + img1.name)
        web.ctx.orm.delete(img1)
        raise web.seeother("/article/edit/%s" % img1.article.id)


class memories:
    def GET(self):
        '''
        catalogs = web.ctx.orm.query(Catalog).filter_by(channel=2).order_by(Catalog.weight).all()
        for cat in catalogs:
            cat.count = len(cat.article)
        return render.memories(catalogs)
        '''
        raise web.seeother('/articles/catalog/100')


class vedios:
    def GET(self):
        catalogs = web.ctx.orm.query(Catalog).filter(Catalog.channel == 3).order_by(Catalog.weight).all()
        return render.vedios(catalogs)


class vedio_create:
    @login_required
    def GET(self):
        catalogs = web.ctx.orm.query(Catalog).filter(Catalog.channel == 3).order_by(Catalog.name).all()
        return render.vedio_create(catalogs)

    @login_required
    def POST(self):
        d = web.input()
        print d
        v1 = Vedio(d)
        web.ctx.orm.add(v1)
        raise web.seeother('/vedios')


class vedio_edit:
    @login_required
    def GET(self, id):
        vedio = web.ctx.orm.query(Vedio).filter_by(id=id).one()
        catalogs = web.ctx.orm.query(Catalog).filter(Catalog.channel == 3).order_by(Catalog.name).all()
        return render.vedio_edit(vedio, catalogs)

    @login_required
    def POST(self, id):
        d = web.input()
        if d.submit == u"修改视频":
            v = web.ctx.orm.query(Vedio).filter_by(id=id).one()
            v.update(d)
            web.ctx.orm.add(v)
            raise web.seeother('/vedios')
        if d.submit == u"删除视频":
            v = web.ctx.orm.query(Vedio).filter_by(id=id).one()
            web.ctx.orm.delete(v)
            raise web.seeother('/vedios')


class vedio_view:
    def GET(self, id):
        vedio = web.ctx.orm.query(Vedio).filter_by(id=id).one()
        return render.vedio_view(vedio)


class activity:
    def GET(self):
        return render.activity()
