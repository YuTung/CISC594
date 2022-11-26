
import globalVariables
import socket


class UserStatus():
        
    def change_status_button_display(self, txt):
        if txt == "Online":
            txt = "Do not disturb"
        elif txt == "Do not disturb":
            txt = "Offline"
        else:
            txt = "Online"
        return txt
        
        
    def update_status_on_server(self, txt):
        msg = "status_encode\n"
        msg = msg + txt
        try:
            globalVariables.client.send(msg.encode())
        except:
            pass
        #print(msg)
        return msg