# coding: utf-8

import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.web, tornado.gen
import tornado.escape
import tornado.log
import logging
import os, hashlib, base64
import secrets

import datetime
import zoneinfo
import apsw
import passlib.handlers.argon2


stock_cookie = secrets.token_hex(32)

conn = apsw.Connection("...")
cur = conn.cursor()



class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header("Server", "Alien 2.0 for static")


class BossHandler(tornado.web.RequestHandler):
    @tornado.web.removeslash
    def get_current_user(self):
        return self.get_secure_cookie("boss")
    


class IndexAdmin(tornado.web.RequestHandler):
    async def get(self):
        self.set_header("Server", "Alien 2.0")
        self.render("admin/login-boss.html")


class LoginBoss(tornado.web.RequestHandler):
    async def post(self):
        self.set_header("Server", "Alien 2.0")
        now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("Africa/Algiers"))
        idd = self.get_argument("login").lower()
        password = self.get_argument("pwd")
        with conn:
            cur.execute('SELECT * FROM `boss` WHERE `id`=?;', (idd,))
            passwd = cur.fetchone()
            try :
                if (passlib.handlers.argon2.argon2.verify(password, passwd[1])):
                    user = {"id": passwd[0], "nom": passwd[2], "last": str(now), "bus": passwd[4], "country": passwd[-4], "gerant": passwd[-3]}
                    self.set_secure_cookie('boss', tornado.escape.json_encode(user))
                    self.redirect("/admin/caisse")
                else:
                    self.write("baaaad")
            except TypeError as e:
                self.write(str(e))


class CaisseBoss(BossHandler):
    @tornado.web.authenticated
    async def get(self):
        self.set_header("Server", "Alien 2.0")
        me = tornado.escape.json_decode(self.get_secure_cookie("boss"))
        caisse = self.request.uri.split("=")
        now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("Africa/Algiers"))
        
        self.render("admin/caisse.html", foo=123)


class VentesPan(BossHandler):
    @tornado.web.authenticated
    async def get(self, idd):
        self.set_header("Server", "Alien 2.0")
        me = tornado.escape.json_decode(self.get_secure_cookie("boss"))
        now =  datetime.datetime.now(tz=zoneinfo.ZoneInfo("Africa/Algiers"))
    
        cur.execute('''
        SELECT
        ;
        ''', (idd, ) )
        produits = cur.fetchall()
                


urls = [
    (r"/admin/boss", IndexAdmin),
    (r"/admin/login", LoginBoss),
    (r"/admin/caisse", CaisseBoss),
    (r"/admin/panier/([^/]+)?", VentesPan),    
    (r"/(.*)", MyStaticFileHandler, {"path":r"{0}".format(os.path.join(os.path.dirname(__file__),"static"))}),
]


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

# tornado.options.define("port", default=8000, help="port to listen on")
tornado.options.define("ip", default='127.0.0.1', help="IP")


log_file = "/logs/app.log"
formatter = tornado.log.LogFormatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Hh%M_%d-%m-%Y')
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1048576, backupCount=100)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


cur.execute("SELECT * from app")
serie = cur.fetchone()

tornado.options.parse_command_line()
logging.info("There you go to the Aicignaaaaaa")
application = tornado.web.Application(urls,**settings)
server = tornado.httpserver.HTTPServer(application)
server.listen(8000, tornado.options.options.ip)
tornado.ioloop.IOLoop.instance().start()