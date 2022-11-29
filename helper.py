import threading
from datetime import datetime

def format_msg_info():
   tid = threading.get_ident()
   now = datetime.now() # current date and time
   date_time = now.strftime("%m/%d/%Y %H:%M:%S")
   info = '\n\n%s [%d]\n' % (date_time, tid)
   return info

def format_print(msg):
   tid = threading.get_ident()
   now = datetime.now() # current date and time
   date_time = now.strftime("%m/%d/%Y %H:%M:%S")
   log = '%s [%d]: %s' % (date_time, tid, msg)
   print(log)
