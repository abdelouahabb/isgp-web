import asyncio
import tornado
import os
import secrets

stock_cookie = secrets.token_hex(32)

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header("Server", "angem.dz")

class Index(tornado.web.RequestHandler):
    def get(self):
        self.write("je suis dans index")

class Bonjour(tornado.web.RequestHandler):
    def get(self):
        self.write("je suis dans bonjour")

class Bonsoir(tornado.web.RequestHandler):
    def get(self):
        self.render("angem.html")

class Salut(tornado.web.RequestHandler):
    def post(self):
        nom = self.get_argument("nom")
        self.redirect("http://angem.dz")

urls = ([
        (r"/inscription", Index),
        (r"/login", Bonjour),
        (r"/angem", Bonsoir),
        (r"/information", Salut),
        (r"/(.*)", MyStaticFileHandler, {"path":r"{0}".format(os.path.join(os.path.dirname(__file__),"static"))}),
    ])

settings = dict({
    "template_path": os.path.join(os.path.dirname(__file__),"templates"),
    "static_path": os.path.join(os.path.dirname(__file__),"static"),
    "static_handler_class":MyStaticFileHandler,
    "static_hash_cache": False,
    "cookie_secret": stock_cookie,
    "xsrf_cookies": True,
    "debug": True,
    # "debug": False,
    "compress_response": True,
    "login_url": "/admin/boss"

})

application = tornado.web.Application(urls,**settings)
server = tornado.httpserver.HTTPServer(application)
server.listen(8888, "127.0.0.1")
tornado.ioloop.IOLoop.instance().start()
