import tornado.ioloop
import tornado.web
import tornado
import tornado_mysql
from tornado import gen
import tornado.ioloop
import tornado.web
import os.path
import tornado.auth
import uuid
import tormysql
import pymysql

# GET_ARGUMENT ITU KETIKA ADA VARIABLE DI URI
# %S BUAT STRING %D BUAT INTEGER
# JADINYA PAKE PYMYSQL, KARENA TORNADO MYSQL POOL NYA KE CLOSE SENDIRI
#


db = pymysql.connect("localhost","root","","tornado_test")

# pymysql.connect('','')
#
# pool = tormysql.ConnectionPool(
#     max_connections = 20, #max open connections
#     idle_seconds = 7200, #conntion idle timeout time, 0 is not timeout
#     wait_connection_timeout = 3, #wait connection timeout
#     host = "127.0.0.1",
#     user = "root",
#     passwd = "",
#     db = "tornado_test",
#     charset = "utf8"
# )
#
# IOLoop = tornado.ioloop.IOLoop.current()
# @gen
def insert_user(stmt,data,id):
    cursor = db.cursor()
    try:
        # sql = "SELECT * FROM USERS WHERE google_id '%d'" % (1000)
        sql = "SELECT * FROM USERS WHERE google_id = '%s'" % (id)
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        print('coba',results)
        if(len(results)==0):
            cursor.execute(stmt, data)
        db.commit()
    except:
        db.rollback()

def insert_photo(stmt,data):
    cursor = db.cursor()
    try:
        cursor.execute(stmt, data)
        db.commit()
    except:
        db.rollback()
# def insert_photo(stmt,data):

    # print('masuk insert user')
    # # with ( pool.Connection()) as conn:
    # with (yield pool.Connection()) as conn:
    #     try:
    #         print('try')
    #         with conn.cursor() as cursor:
    #             yield cursor.execute(stmt, data)
    #             # cursor.execute(stmt, data)
    #             # yield cursor.execute('INSERT INTO USERS(id,name,email,google_id) Values(1,"adhi","adhistria1@gmail.com","123")')
    #     except:
    #         print('except')
    #         yield conn.rollback()
    #         # conn.rollback()
    #     else:
    #         print('else')
    #         # conn.commit()
    #         yield conn.commit()
    # yield pool.close()


__UPLOADS__ = os.path.dirname(__file__)+ "/uploads"

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        # self.write("Hello, world")
        self.render('home.html')

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        # print(self.get_argument('code'))
        # self.get_argument('code','code')
        # settings = dict(
        #     cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        #     google_oauth={"key": '188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.googleusercontent.com', "secret": '5_ljzUmUAJAvzw7IGItrYVP7'},
        # )
        if self.get_argument('code', False):
            print('masuk')
            access = await self.get_authenticated_user(
                redirect_uri='http://localhost:8000/login',
                code=self.get_argument('code'),
            )
            user = await self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            self.set_secure_cookie('user_access_token',access['access_token'])
            print('sampe sini')
            # # print('access token')
            # print('access token', user['access_token'])
            insert_stmt = (
                "INSERT INTO users (name, email, google_id) "
                "VALUES (%s, %s, %s)"
            )
            data = (user['name'], user['email'], user['id'])


            data = insert_user(insert_stmt,data,user['id'])
            print(data)
            print(user)
            print('success')
            self.redirect('/home')
            # self.redirect('/authenticate')

        else:
            await self.authorize_redirect(
                redirect_uri='http://localhost:8000/login',
                client_secret='5_ljzUmUAJAvzw7IGItrYVP7',
                client_id='188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.googleusercontent.com',
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})

            # user = await self.get_authenticated_user(
            #     redirect_uri='http://localhost:8000/home')
            # print(user)
            # print self.get_authenticated_user(
            #     # callback=
            # )

# class InfoUserHandler(tornado.web.RequestHandler,tornado.auth.GoogleOAuth2Mixin):
#     def get(self):
#         user = self.get_authenticated_user(
#             redirect_uri='http://localhost:8000/home',
#             code=self.get_argument('code'),
#         )
#         print('access token')
#         print('access token',user['access_token'])
#         self.set_secure_cookie(user.access_token)
#         print(user)

class UploadFileHandler(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open((__UPLOADS__+'/'+cname), 'wb')
        # fh = open((__UPLOADS__+'/'+cname), 'w') untuk python 2
        fh.write(fileinfo['body'])
        # self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)
        self.redirect('/home')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
        # if(self.get_argument('code', False)):
        #     print('something wrong')
        # else:
        #     print('True cuy')
        # self.write(greeting)
# class Main():
#     def __init__(self):
#         self.app= tornado.web.Application(handlers =[
#                 (r"/",IndexHandler),
#                 (r"/login",GoogleOAuth2LoginHandler),
#                 (r"/home",HomeHandler),
#                 (r"/upload",UploadFileHandler),
#                 # (r"/index",IndexHandler),
#                 # (r"/info",InfoUserHandler)
#             ],
#             template_path=os.path.join(os.path.dirname(__file__), "views"),
#             cookie_secret = 'cookiesupersecret',
#             google_oauth={"key": '188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.googleusercontent.com',
#                           "secret": '5_ljzUmUAJAvzw7IGItrYVP7'})
#         self.app.listen(8000)
#         IOLoop.start()
#         # self.IOLoop = tornado.ioloop.IOLoop.current()
        # self.IOLoop.start()
def main():
    app = tornado.web.Application(handlers =[
        (r"/",IndexHandler),
        (r"/login",GoogleOAuth2LoginHandler),
        (r"/home",HomeHandler),
        (r"/upload",UploadFileHandler),
        # (r"/index",IndexHandler),
        # (r"/info",InfoUserHandler)
    ],
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret = 'cookiesupersecret',
        google_oauth={"key": '188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.googleusercontent.com',
                      "secret": '5_ljzUmUAJAvzw7IGItrYVP7'}
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()