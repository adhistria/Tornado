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
import datetime
from PIL import Image,ImageFile
import configparser

# GET_ARGUMENT ITU KETIKA ADA VARIABLE DI URI
# %S BUAT STRING %D BUAT INTEGER
# JADINYA PAKE PYMYSQL, KARENA TORNADO MYSQL POOL NYA KE CLOSE SENDIRI
#
__UPLOADS__ = os.path.dirname(__file__)+ "/uploads"
__CONFIG__ = configparser.ConfigParser()

# class Database2():
#     def __init__(self):
#         self.user = __CONFIG__['DEFAULT'] ['db_user']
#         self.password = __CONFIG__['DEFAULT'] ['db_password']
#         self.host = __CONFIG__['DEFAULT'] ['db_host']
#         self.db_name = __CONFIG__['DEFAULT'] ['db_name']
#         self.db = pymysql.connect(self.host,self.user,self.password,self.db_name)
#         self.cursor = self.db.cursor()
#     def insert_user(self,data,id):
#         try:
#             sql = "SELECT EMAIL FROM USERS WHERE google_id = '%s'" % (id)
#             cursor.execute(sql)
#             results = cursor.fetchall()
#             if (len(results) == 0):
#                 print('bener 0')
#                 stmt = (
#                     "INSERT INTO users (name, email, google_id) "
#                     "VALUES (%s, %s, %s)"
#                 )
#                 cursor.execute(stmt, data)
#             db.commit()
#         except:
#             db.rollback()



db = pymysql.connect("localhost", "root", "", "tornado_test")
cursor = db.cursor()

def insert_user(data,id):

    try:
        sql = "SELECT EMAIL FROM USERS WHERE google_id = '%s'" % (id)
        cursor.execute(sql)
        results = cursor.fetchall()
        if(len(results)==0):
            print('bener 0')
            stmt = (
                "INSERT INTO users (name, email, google_id) "
                "VALUES (%s, %s, %s)"
            )
            cursor.execute(stmt, data)
        db.commit()
    except:
        db.rollback()

# def get_user_id(google_id):
#     try:
#         sql = "SELECT ID FROM USERS WHERE google_id = '%s'" % (google_id)
#         cursor.execute(sql)
#         results = cursor.fetchone()
#         db.commit()
#         return results[0]
#     except:
#         db.rollback()

def insert_photo(file_name,id):
    print(file_name)
    try:
        print('masuk try')
        stmt= "INSERT INTO PHOTOS(filename,user_id) VALUES('%s','%d')" % (file_name,id)
        cursor.execute(stmt)
        db.commit()
    except:
        print('gagal')
        db.rollback()

# def get_photos():
#     try:
#         stmt = "SELECT FILENAME FROM PHOTOS WHERE USER_ID = ('%s')" %
class UserInfoHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        user = await self.oauth2_request(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            access_token=self.get_secure_cookie('user_access_token'))
        self.set_secure_cookie('email',user['email'])
        self.set_secure_cookie('user_id',user['id'])
        data = (user['name'], user['email'], user['id'])
        insert_user(data, user['id'])
        self.redirect('/home')

class CallbackHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        access = await self.get_authenticated_user(
            redirect_uri='http://localhost:8000/callback',
            code=self.get_argument('code'),
        )
        # user = await self.oauth2_request(
        #     "https://www.googleapis.com/oauth2/v1/userinfo",
        #     access_token=access["access_token"])
        # # print(access)
        # print(user)
        # self.set_secure_cookie('email',user['email'])
        # self.set_secure_cookie('user_id',user['id'])
        self.set_secure_cookie('user_access_token', access['access_token'])
        # print(user['id'])
        # data = (user['name'], user['email'], user['id'])
        # insert_user(data,user['id'])
        self.redirect('/user_info')

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        # self.write("Hello, world")
        self.render('home.html')

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        await self.authorize_redirect(
            redirect_uri='http://localhost:8000/callback',
            client_secret='5_ljzUmUAJAvzw7IGItrYVP7',
            client_id='188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.'
                      'googleusercontent.com',
            scope=['profile', 'email'],
            response_type='code',
            extra_params={'approval_prompt': 'auto'})

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
        try:
            img = Image.open(self.request.files['filearg'][0])
            date_now = datetime.datetime.now()
            str_date = date_now.strftime("%Y-%m-%d")
            img.save("out.jpg", "JPEG", quality=80, optimize=True,
                     progressive=True)

            # do stuff
        except IOError:
            # filename not an image file
            # add flash
            self.redirect('/home')

        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        insert_photo(cname)
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
    __CONFIG__.read('config.ini')
    app = tornado.web.Application(handlers =[
        (r"/",IndexHandler),
        (r"/login",GoogleOAuth2LoginHandler),
        (r"/user_info",UserInfoHandler),
        (r"/callback",CallbackHandler),
        (r"/home",HomeHandler),
        (r"/upload",UploadFileHandler),
        # (r"/index",IndexHandler),
        # (r"/info",InfoUserHandler)
    ],
        template_path=__CONFIG__['DEFAULT']['template_path'],
        # static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret = 'cookiesupersecret',
        google_oauth={"key": __CONFIG__['DEFAULT']['google_client_id'],
                      "secret": __CONFIG__['DEFAULT']['google_client_secret']}
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # print(config['DEFAULT']['upload_path'])
    # print(config['DEFAULT']['key'])
    # print(config['DEFAULT']['UPLOAD_PATH'])
    # topsecret = config['DEFAULT']
    # print(topsecret['UPLOAD_PATH'])
    # print(__UPLOADS__)
    # main()