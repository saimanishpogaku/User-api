import mysql.connector
import os
import settings
class Connection(object):
  def __init__(self):
    try:
      self.conn = mysql.connector.connect(
      host=os.getenv("HOST"),
      user=os.getenv("USER_NAME"),
      password=os.getenv("PASSWORD"),
      db=os.getenv("DBNAME")
      )
    except Exception as e:
      print("Database issue due to {} ".format(e.msg))
      self.conn = None   

user_db = Connection().conn
# print(conn)
print(os.getenv("HOST"))
print(os.getenv("USER_NAME"))
print(os.getenv("PASSWORD"))


