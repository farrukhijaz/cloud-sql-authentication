#!/usr/bin/env python
import os
import tornado.web
import tornado.ioloop
import tornado.options
from tornado import gen
import tornado.httpserver
import psycopg2
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        title = "Hello, World!"
        bgcolor = "dodgerblue"
        self.render("template.html", title=title, bgcolor=bgcolor)
        print(self.request)
class ProbeHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            authtype = "K8 Secrets"
            db_user = os.environ.get('DB_USER')
            db_pwd = os.environ.get('DB_PWD')
            db = psycopg2.connect("host=localhost sslmode=disable dbname=studio user=%s password=%s" % (db_user,db_pwd))
            cursor = db.cursor()
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            title = "Cloud SQL DB version is: %s" % result
            dbuser = "username used to connect to DB: %s" % db_user
            bgcolor = "yellow"
            print(title)
            self.set_status(200)
        except ValueError: 
            title = "Please set the environment variable DB_USER"
            bgcolor = "darkred"
            self.set_status(503)
        except Exception as err:
            # pass exception to function
            print_psycopg2_exception(err)
            bgcolor = "darkred"
            self.set_status(503)
        except OperationalError as e:
            print_psycopg2_exception(e)
            bgcolor = "darkred"
            self.set_status(503)
        self.render("template.html", title=title, bgcolor=bgcolor, dbuser=dbuser, authtype=authtype)

def make_app():
    return tornado.web.Application([
        (r"/k8-secret-auth", ProbeHandler),
        (r"/isalive", ProbeHandler),
        (r"/isready", ProbeHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
