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
		self.migrate_users()
		self.migrate_photos()


	def insert_user(self, data, id):
		# cursor = cursor()
		try:
			sql = "SELECT EMAIL FROM USERS WHERE google_id = '%s'" % (id)
			self.cursor.execute(sql)
			results = self.cursor.fetchall()
			print('ini result',results)
			print(len(results))
			if (len(results) == 0):
				stmt = ("INSERT INTO USERS(NAME, EMAIL, GOOGLE_ID) "
				        "VALUES ('%s', '%s', '%s')" % (data))
				self.cursor.execute(stmt)
			self.db.commit()
		except:
			self.db.rollback()

	def insert_photo(self, data):
		try:
			stmt = ("INSERT INTO PHOTOS(FILENAME, SIZE, DIMENSION, USER_ID) " 
				   "VALUES('%s','%d','%s','%d')" % (data))
			self.cursor.execute(stmt)
			self.db.commit()
		except:
			self.db.rollback()

	def get_user_id(self, email):
		try:
			stmt = ("SELECT ID FROM USERS WHERE EMAIL = ('%s')" % (email))
			self.cursor.execute(stmt)
			result = self.cursor.fetchone()
			return result[0]
		except:
			return 'unable to fetch data'

	def get_photos(self,id):
		try:
			stmt = ("SELECT * FROM PHOTOS WHERE USER_ID = '%d'" % (id))
			self.cursor.execute(stmt)
			results = self.cursor.fetchall()
			return results
		except:
			return 'unable to fetch data'

	def migrate_users(self):
		try:
			stmt = """CREATE TABLE IF NOT EXISTS USERS ( 
			       ID INT(11) NOT NULL AUTO_INCREMENT, 
			       NAME VARCHAR(50) , 
			       EMAIL VARCHAR(50) NOT NULL, 
			       GOOGLE_ID CHAR(30) NOT NULL, 
			       PRIMARY KEY(ID))"""
			self.cursor.execute(stmt)
			self.db.commit()
		except:
			self.db.rollback()

	def migrate_photos(self):
		try:
			stmt = """CREATE TABLE IF NOT EXISTS PHOTOS ( 
			       ID INT(11) NOT NULL ,
			       FILENAME VARCHAR(100),
			       SIZE INT(11),
			       DIMENSION VARCHAR(20),
			       USER_ID INT NOT NULL,
			       PRIMARY KEY(ID),
			       FOREIGN KEY (USER_ID) REFERENCES USERS(ID))"""
			self.cursor.execute(stmt)
			self.db.commit()
		except:
			self.db.rollback()