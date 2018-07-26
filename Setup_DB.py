import configparser
import pymysql


__CONFIG__ = configparser.ConfigParser()
__CONFIG__ .read('config.ini')

class Database():
	def __init__(self):
		self.user = __CONFIG__['DEFAULT']['db_user']
		self.password = __CONFIG__['DEFAULT']['db_password']
		self.host = __CONFIG__['DEFAULT']['db_host']
		self.db_name = __CONFIG__['DEFAULT']['db_name']
		self.db = pymysql.connect(self.host,self.user,self.password,self.db_name)
		self.cursor = self.db.cursor()

	def insert_user(self, data, id):
		# cursor = cursor()
		try:
			sql = "SELECT EMAIL FROM USERS WHERE google_id = '%s'" % (id)
			self.cursor.execute(sql)
			results = self.cursor.fetchall()
			if (len(results) == 0):
				stmt = ("INSERT INTO users (name, email, google_id) "
						"VALUES (%s, %s, %s)")
				self.cursor.execute(stmt, data)
				self.db.commit()
		except:
			self.db.rollback()

	def insert_photo(self,file_name,email):
		print('test insert')
		try:
			print('email',email)
			stmt = ("INSERT INTO PHOTOS(filename,user_email) " 
				   "VALUES('%s','%s')" % (file_name, email))

			self.cursor.execute(stmt)
			self.db.commit()
		except:
			self.db.rollback()