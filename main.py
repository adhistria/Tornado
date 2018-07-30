import tornado.ioloop
import tornado.web
import tornado
import tornado.ioloop
import tornado.web
import os.path
import tornado.auth
import os
import datetime
import hashlib
from PIL import Image,ImageFile
import configparser
from io import StringIO,BytesIO
from Setup_DB import Database
from User import User

# OBJECT USER GA GUNA
__DB__ = Database()
__CONFIG__ = configparser.ConfigParser()
# __USER__ = User()

def check_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def check_auth(check):
    return check.get_secure_cookie('user_access_token')

# def check_message(check):
#     if(check.get_cookie)

def hash_sha1(file_name):
    file_name = file_name.encode(encoding='UTF-8', errors='strict')
    hash_name = hashlib.sha1(file_name)
    hash_name.hexdigest()
    hex_hash_name = hash_name.hexdigest()
    return hex_hash_name

def get_folder_name(file_name):
    extn = os.path.splitext(file_name)[1]
    date_now = datetime.datetime.now()
    str_date = date_now.strftime("%Y-%m-%d")
    upload_path = '/'.join([__CONFIG__['DEFAULT']['upload_path'],str_date])
    check_dir(upload_path)
    hex_hash_name = hash_sha1(file_name)
    upload_path = '/'.join([upload_path, hex_hash_name[0:2]])
    check_dir(upload_path)
    img_name = str_date + '_' + hex_hash_name + extn
    return upload_path, img_name

def write_file(upload_path, new_name, fileinfo, id, size, dimension):
    fh = open('/'.join([upload_path, new_name]), 'wb')
    fh.write(fileinfo['body'])
    data = (new_name, size, dimension, id)
    # __DB__.insert_photo(new_name, email)
    # __DB__.insert_photo(new_name, id)
    __DB__.insert_photo(data)
    fh.close()

def write_progressive_file(upload_path, new_name, width):
    fh = open('/'.join([upload_path, new_name]), 'rb')
    img = Image.open(fh)
    size = 1280, 1280
    if(width > int(__CONFIG__['DEFAULT']['image_maximum_width'])):
        img.thumbnail(size,Image.ANTIALIAS)
    new_name = os.path.splitext(new_name)[0]
    img_save_path = '/'.join([upload_path, new_name + '.progressive.jpeg'])
    img.save(img_save_path, "JPEG", quality=80, optimize=True, progressive=True)
    fh.close()

def write_thumbnail_file(upload_path, new_name):
    size = 128, 128
    fh = open('/'.join([upload_path, new_name]), 'rb')
    img = Image.open(fh)
    img.thumbnail(size, Image.ANTIALIAS)
    new_name = os.path.splitext(new_name)[0]
    img_save_path = '/'.join([upload_path, new_name + '.thumbnail.jpeg'])
    img.save(img_save_path,quality=100, optimize=True)

class LogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie('email')
        self.clear_cookie('user_id')
        self.clear_all_cookies()
        self.redirect('/')

class UserInfoHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        user = await self.oauth2_request(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            access_token=self.get_secure_cookie('user_access_token'))
        data = (user['name'], user['email'], user['id'])
        __DB__.insert_user(data, user['id'])
        user_id = __DB__.get_user_id(user['email'])
        self.set_cookie('user_id', str(user_id))
        self.set_cookie('email', user['email'])
        self.redirect('/home')

class CallbackHandler(tornado.web.RequestHandler,
                      tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        access = await self.get_authenticated_user(
            redirect_uri = 'http://localhost:8000/callback',
            code = self.get_argument('code'),
        )
        self.set_secure_cookie('user_access_token', access['access_token'])
        self.redirect('/user_info')

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        if check_auth(self) is None:
            self.redirect('/')
        else:
            photos = get_photos(int(self.get_cookie('user_id')))
            self.render('home.html', photos=photos)


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
        new_img = fileinfo['body']
        size_img = len(new_img)
        try:
            file_name = fileinfo['filename']
            img = Image.open(BytesIO(self.request.files['filearg'][0]['body']))
            try:
                img.verify()
            except Exception:
                self.set_cookie('message', 'fail')
                self.redirect('/home')
            width, height = img.size
            dimension = 'x'.join([str(width),str(height)])
            upload_path, new_name = get_folder_name(file_name)
            write_file(upload_path, new_name, fileinfo,
                       int(self.get_cookie('user_id')), size_img, dimension)
            write_progressive_file(upload_path, new_name, width)
            write_thumbnail_file(upload_path,new_name)
            self.set_cookie('message','succes')
            self.redirect('/home')
        except IOError:
            self.set_cookie('message', 'fail')
            self.redirect('/home')
            return

class Photo():
    def __init__(self, name, url, progressive_url, thumbnail_url):
        self.name = name
        self.url = url
        self.progressive_url = progressive_url
        self.thumbnail_url = thumbnail_url
        # self.size = size


# class Photos():
#     def __init__(self):
#         self.photos = []
#     def add_photo(self,photo):
#         self.photos.append(photo)

def get_photos(email):
    photos = __DB__.get_photos(email)
    # all_photo = Photos()
    all_photo = []
    if(len(photos)>0):
        for photo in photos:
            img_url, img_progressive_url, img_thumbnail \
                = extract_folder_photo(photo[1])
            photo = Photo(photo[1], img_url, img_progressive_url, img_thumbnail)
            all_photo.append(photo)
    return all_photo


def extract_folder_photo(name):
    folder_name = name[:10]
    sub_folder_name = name[11:13]
    raw_url_photo =  '/'.join([folder_name,sub_folder_name,name])
    raw_url = raw_url_photo
    raw_url_photo = os.path.splitext(raw_url_photo)[0]
    raw_url_photo_progressive = raw_url_photo + '.progressive.jpeg'
    raw_url_photo_thumbnail = raw_url_photo + '.thumbnail.jpeg'
    return raw_url,raw_url_photo_progressive, raw_url_photo_thumbnail

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
class CobaLogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('dashboard.html')

def main():
    __CONFIG__.read('config.ini')
    app = tornado.web.Application(handlers=[
        (r"/", IndexHandler),
        # (r"/",IndexHandler2),
        (r"/login",GoogleOAuth2LoginHandler),
        (r"/user_info",UserInfoHandler),
        (r"/callback",CallbackHandler),
        (r"/home", HomeHandler),
        # (r"/static/(.*)", tornado.web.StaticFileHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
         {'path':__CONFIG__['DEFAULT']['upload_path']}),
        # (r"/images/(.*)", tornado.web.StaticFileHandler,
        #  {'path': "/tmp"}),
        # (r"/home",CobaLogoutHandler),
        (r"/upload",UploadFileHandler),
        (r"/logout",LogoutHandler),
    ],
        template_path = __CONFIG__['DEFAULT']['template_path'],
        # static_url_prefix = __CONFIG__['DEFAULT']['upload_path'],
        static_path = __CONFIG__['DEFAULT']['upload_path'],
        cookie_secret = 'cookiesupersecret',
        google_oauth = {"key": __CONFIG__['DEFAULT']['google_client_id'],
                      "secret": __CONFIG__['DEFAULT']['google_client_secret']},


    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()