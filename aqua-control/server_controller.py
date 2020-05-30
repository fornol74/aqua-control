from pymemcache.client import base
import cherrypy
import os
import os.path

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

client = base.Client(('127.0.0.1', 11211))
# ini_reload = False


class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


class AquaControlServer(object):
    # ini_reload = False

    @cherrypy.expose
    def index(self, file=""):
        # self.ini_reload = False
        # global ini_reload
        out = """<html>
      <body>
        <form id="usrform" action = "/" method="POST">
        <textarea form="usrform" id = "textarea" name = "file" rows = "30" cols = "50" wrap = "off">%s</textarea>
        <input type="submit" value="Submit" form="usrform"></value>
        </form>
      </body>
      </html>"""

        # print(file)

        if file != "":
            path = os.path.join(absDir, "config.ini")
            f = open(path, 'w')
            f.write(file)
            f.close()
            # print("inside")
            # ini_reload = True
            # print(ini_reload)

        path = os.path.join(absDir, "config.ini")
        f = open(path, 'r')
        file_read = f.read()
        f.close()

        # print(file_read)
        # cherrypy.session['test'] = 'dupa2'
        client.set('ini_reload', 'true')
        # cherrypy.config.update({'tools.sessions.on': True})

        return out % (file_read)

    # @cherrypy.expose
    # def ini_reload(self):
    #     # print(cherrypy.session['test'])
    #     return cherrypy.session['test']
