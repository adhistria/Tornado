import tornado.ioloop
import tornado.web
import tornado
import tornado.ioloop
import tornado.web
import os.path
import tornado.auth
import os
import pymysql
import datetime
import hashlib
from PIL import Image,ImageFile
import configparser
from io import StringIO,BytesIO
from Setup_DB import Database
# GET_ARGUMENT ITU KETIKA ADA VARIABLE DI URI
# %S BUAT STRING %D BUAT INTEGER
# JADINYA PAKE PYMYSQL, KARENA TORNADO MYSQL POOL NYA KE CLOSE SENDIRI
# CEK WIDTH
__DB__ = Database()
__CONFIG__ = configparser.ConfigParser()


def check_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def check_auth(check):
    return check.get_secure_cookie('user_access_token')

def get_folder_name(file_name):
    date_now = datetime.datetime.now()
    str_date = date_now.strftime("%Y-%m-%d")
    file_name = file_name.encode(encoding='UTF-8', errors='strict')
    hash_name = hashlib.sha1(file_name)
    hash_name.hexdigest()
    hash_name_hex = hash_name.hexdigest()
    upload_path = '/'.join([__CONFIG__['DEFAULT']['upload_path'],str_date])
    print('upload_path',upload_path)
    check_dir(upload_path)
    upload_path = '/'.join([upload_path,hash_name_hex[0:2]])
    check_dir(upload_path)
    img_name = str_date + '_' + hash_name_hex + '.jpeg'
    check_dir(upload_path)
    return upload_path, img_name

class LogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_all_cookies()

# def get_photos():
#     try:
#         stmt = "SELECT FILENAME FROM PHOTOS WHERE USER_ID = ('%s')" %
class UserInfoHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        user = await self.oauth2_request(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            access_token=self.get_secure_cookie('user_access_token'))
        self.set_cookie('email',user['email'])
        self.set_secure_cookie('user_id',user['id'])
        data = (user['name'], user['email'], user['id'])
        __DB__.insert_user(data, user['id'])
        self.redirect('/home')

class CallbackHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        access = await self.get_authenticated_user(
            redirect_uri='http://localhost:8000/callback',
            code=self.get_argument('code'),
        )
        self.set_secure_cookie('user_access_token', access['access_token'])
        self.redirect('/user_info')

class HomeHandler(tornado.web.RequestHandler):
    async def get(self):
        if check_auth(self) is None:
            self.redirect('/')
        else:
            data = await (self.flush('fail'))
            print(data)
            self.render('home.html')


class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        await self.authorize_redirect(
            redirect_uri = 'http://localhost:8000/callback',
            client_secret = '5_ljzUmUAJAvzw7IGItrYVP7',
            client_id = '188260276961-vnct27bserf5blt209hmt9p16g0ihm0t.apps.'
                      'googleusercontent.com',
            scope = ['profile', 'email'],
            response_type = 'code',
            extra_params = {'approval_prompt': 'auto'})

class UploadFileHandler(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        print(fileinfo)
        new_img = fileinfo['body']
        size_img = len(new_img)
        try:
            file_name = fileinfo['filename']
            img = Image.open(BytesIO(self.request.files['filearg'][0]['body']))
            try:
                img.verify()
            except Exception:
                self.set_cookie('message','fail')
                self.redirect('/home')
            upload_path,new_name = get_folder_name(file_name)
            fh = open('/'.join([upload_path, new_name]), 'wb')
            fh.write(fileinfo['body'])
            __DB__.insert_photo(new_name,self.get_cookie('email'))
            fh.close()
            fh = open('/'.join([upload_path, new_name]), 'rb')
            img = Image.open(fh)
            img_save_path = '/'.join([upload_path, new_name + '.progressive.jpeg'])
            print('image : ',img_save_path)
            img.save(img_save_path, "JPEG", quality=80, optimize=True, progressive=True)
            self.set_cookie('message','succes')
        except IOError:
            self.set_cookie('message', 'fail')
            self.redirect('/home')
            return

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        if check_auth(self) is None:
            self.render('index.html')
        else:
            self.redirect('/home')

class IndexHandler2(tornado.web.RequestHandler):
    def get(self):
        self.write('cobain boy')
        self.render('index.html')

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
    app = tornado.web.Application(handlers=[
        (r"/", IndexHandler),
        # (r"/",IndexHandler2),
        (r"/login",GoogleOAuth2LoginHandler),
        (r"/user_info",UserInfoHandler),
        (r"/callback",CallbackHandler),
        (r"/home",HomeHandler),
        (r"/upload",UploadFileHandler),
        (r"/logout",LogoutHandler),
    ],
        template_path = __CONFIG__['DEFAULT']['template_path'],
        cookie_secret = 'cookiesupersecret',
        google_oauth = {"key": __CONFIG__['DEFAULT']['google_client_id'],
                      "secret": __CONFIG__['DEFAULT']['google_client_secret']}
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()