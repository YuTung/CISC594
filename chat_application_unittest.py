import unittest

import socket
from TypeIndicatorClass import TypeIndicator
from UserStatusClass import UserStatus
import time
from datetime import datetime
import globalVariables
from server_gui import get_client_index, update_client_names_display
import threading
from helper import format_msg_info

class TestTypeIndicator(unittest.TestCase):

    def setUp(self):
        self.type_indicator = TypeIndicator()

    def test_key_pressed(self):
        self.last_press_time = 0
        msg_out = self.type_indicator.key_pressed()
        self.assertEqual(msg_out, "type_indicator_encode", 'wrong msg for large delta_t')
        
        self.last_press_time = time.time()
        msg_out = self.type_indicator.key_pressed()
        self.assertEqual(msg_out, "", 'wrong msg for small delta_t')
        
    def test_key_released(self):
        msg_out = self.type_indicator.key_released()
        self.assertEqual(msg_out, "type_indicator_release_encode", 'wrong msg for key released')
    
    
class TestUserStatus(unittest.TestCase):

    def setUp(self):
        self.user_status = UserStatus()
        
    def test_change_button_display(self):
        txt = "Online"
        out_txt = self.user_status.change_status_button_display(txt)
        self.assertEqual(out_txt, "Do not disturb", 'wrong status')
        
        
        txt = "Do not disturb"
        out_txt = self.user_status.change_status_button_display(txt)
        self.assertEqual(out_txt, "Offline", 'wrong status')
        
        
        txt = "Offline"
        out_txt = self.user_status.change_status_button_display(txt)
        self.assertEqual(out_txt, "Online", 'wrong status')
            
         
    def test_update_status_on_server(self):      
        txt = "new_status"
        out_txt = self.user_status.update_status_on_server(txt)
        
        self.assertEqual(out_txt, "status_encode\nnew_status", 'wrong msg : status with tag')
        
class TestConnectAndMessage(unittest.TestCase):
   def setUp(self):
       pass

   def test_connect(self):
       # start server
       globalVariables.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       globalVariables.server.bind((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       globalVariables.server.listen(5)  # server is listening for client connection
       print("server started")

       globalVariables.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       globalVariables.client.connect((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       globalVariables.client.send("test".encode())  # Send name to server after connecting
       print("client connected")

   def read_message(self, read_client):

       read_client.connect((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       while True:
           try:
               print("read message")
               data = read_client.recv(4096).decode()
               print("get message")
               print(data)
           except Exception as e:
               print(e)
               print("no message")
               break


   def test_connect_and_send_message(self):
       # start server
       globalVariables.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       globalVariables.server.bind((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       globalVariables.server.listen(5)  # server is listening for client connection
       print("server started")

       read_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       threading._start_new_thread(self.read_message, (read_client,))
       time.sleep(5)


       client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       client1.connect((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       client1.send("client1".encode())  # Send name to server after connecting
       print("client1 connected")
       client1.shutdown(socket.SHUT_WR)



       client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       client2.connect((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
       client2.send("client2".encode())  # Send name to server after connecting
       # send message to client1
       client2.send("Hi from client2".encode())
       print("client2 connected")
       # time.sleep(15)

       client1.close()
       client2.close()
       globalVariables.server.close()

       # client_msg = str(msg)
       # globalVariables.client.send(client_msg.encode())
       # print("Sending message")


class TestServerMethods(unittest.TestCase):
    def setUp(self):
       self.clients = [1, 2, 3, 4, 5]


    def test_format_msg_info(self):
       msg_info = format_msg_info()
       tid = str(threading.get_ident())
       now = datetime.now() # current date and time
       date_time = now.strftime("%m/%d/%Y %H:%M:%S")
       #self.assertEqual(msg_info.split(' '), [date_time, tid])
       self.assertTrue(date_time in msg_info)
       self.assertTrue(tid in msg_info)

    def test_get_client_index(self):
       clients = [2, 1, 4, 0, 3]
       client = 2
       self.assertEqual(get_client_index(clients, client), 0)
       # empty list
       clients = []
       client = 5
       self.assertEqual(get_client_index(clients, client), -1)

    def test_update_client_names_display(self):
       name_list = ['User1', 'User2', 'User3']
       status_list = ['Online', 'Offline', 'Do not disturb']
       expected = 'User1 : Online\nUser2 : Offline\nUser3 : Do not disturb\n'
       self.assertEqual(update_client_names_display(name_list, status_list), expected)    

if __name__ == '__main__':
    unittest.main()