#!/usr/bin/env python
import os
import tornado.web
import tornado.ioloop
import tornado.options
from tornado import gen
import tornado.httpserver
import psycopg2
from google.cloud import secretmanager

    
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        title = "Hello, World!"
        bgcolor = "dodgerblue"
        self.render("template.html", title=title, bgcolor=bgcolor)
        print(self.request)
class ProbeHandler(tornado.web.RequestHandler):
    def access_secret_version(self, project_id, secret_id, version_id):
        """
        Access the payload for the given secret version if one exists. The version
        can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
        """

        # Import the Secret Manager client library.
        # from google.cloud import secretmanager

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the secret version.
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version.
        response = client.access_secret_version(name=name)

        # Return the decoded payload.
        return response.payload.data.decode('UTF-8')
    def get(self):
        try:
            authtype = "in Application Authentication"
            db_user = os.environ.get('DB_USER')
            dbpwd = self.access_secret_version("567106206607", "db_pwd", "latest")
            db = psycopg2.connect("host=localhost sslmode=disable dbname=studio user=%s password=%s" % (db_user,dbpwd))
            cursor = db.cursor()
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            title = "Cloud SQL DB version is: %s" % result
            dbuser = "username used to connect to DB: %s" % db_user
            bgcolor = "white"
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
        (r"/app-secret-auth", ProbeHandler),
        (r"/isalive", ProbeHandler),
        (r"/isready", ProbeHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
