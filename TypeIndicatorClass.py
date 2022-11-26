
import socket
import time
import globalVariables

class TypeIndicator():
    def __init__(self):
        self.last_press_time = 0

    def key_pressed(self, event=None):
        msg = ""
        delta_t = time.time() - self.last_press_time # to debounce
        if delta_t > 0.1:
            msg = self.send_type_indicator_to_server()
        self.last_press_time = time.time()
        return msg
        
    def key_released(self, event=None):
        return self.send_type_indicator_release_to_server()

    def send_type_indicator_to_server(self):
        msg = "type_indicator_encode"
        try:
            globalVariables.client.send(msg.encode())
        except:
            pass
        #print("Sending indicator")
        return msg
        
    def send_type_indicator_release_to_server(self):
        msg = "type_indicator_release_encode"
        try:
            globalVariables.client.send(msg.encode())
        except:
            pass
        #print("Sending indicator release")
        return msg