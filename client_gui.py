import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time

import globalVariables
from TypeIndicatorClass import TypeIndicator
from UserStatusClass import UserStatus

window = tk.Tk()
window.title("Client")

topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT, padx=10)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT, padx=10)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT, padx=10)
btnStatus = tk.Button(topFrame, text="Offline", command=lambda : status_button_switch())
btnStatus.pack(side=tk.LEFT)
btnStatus.config(state=tk.DISABLED)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack(side=tk.TOP)

nameStatusText = tk.StringVar()
nameStatusText.set("")
nameStatusLabel = tk.Label(displayFrame, textvariable=nameStatusText).pack(side=tk.TOP)

lblLine2 = tk.Label(displayFrame, text="*********************************************************************").pack(side=tk.TOP)
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)

bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=1, width=35)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10), fill=tk.X)
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))


typingIndicatorText = tk.StringVar()
typingIndicatorText.set("")
typingIndicatorLabel = tk.Label(bottomFrame, textvariable=typingIndicatorText, width=20).pack(side=tk.LEFT, fill=tk.X)
bottomFrame.pack(side=tk.BOTTOM)

type_indicator = TypeIndicator()
tkMessage.bind("<KeyPress>",type_indicator.key_pressed)
tkMessage.bind("<KeyRelease>",type_indicator.key_released)

user_status = UserStatus()

def connect():
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        globalVariables.username = entName.get()
        connect_to_server(globalVariables.username)
    btnStatus.config(state=tk.NORMAL)
    btnStatus['text'] = "Online"

def status_button_switch():
    btnStatus['text'] = user_status.change_status_button_display(btnStatus['text'])
    user_status.update_status_on_server(btnStatus['text'])
    
def connect_to_server(name):
    try:
        globalVariables.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        globalVariables.client.connect((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
        globalVariables.client.send(name.encode()) # Send name to server after connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (globalVariables.client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + globalVariables.HOST_ADDR + " on port: " + str(globalVariables.HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
    while True:
        try:
            from_server = sck.recv(4096).decode()
        except:
            print("server is disconnected")
            break

        if not from_server: break
        
        # check if it is typing indicator
        if " is typing..." in from_server:
            #print("is typing")
            typingIndicatorText.set(from_server)
        elif "type_indicator_release_decode" in from_server:
            #print("not typing")
            typingIndicatorText.set("")   
        elif "name_status_encode" in from_server:        
            msg = from_server.split("\n",1)[1]
            update_client_name_status(msg)     
        elif "status_encode" in from_server: 
            pass       
        elif "BYE!" in from_server:
            break
        else:

            # display message from server on the chat window

            # enable the display area and insert the text and then disable.
            # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
            texts = tkDisplay.get("1.0", tk.END).strip()
            tkDisplay.config(state=tk.NORMAL)
            if len(texts) < 1:
                tkDisplay.insert(tk.END, from_server)
            else:
                tkDisplay.insert(tk.END, "\n\n"+ from_server)

            tkDisplay.config(state=tk.DISABLED)
            tkDisplay.see(tk.END)

        # print("Server says: " +from_server)

    globalVariables.client.close()
    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)

    send_message_to_server(msg)


    
def send_message_to_server(msg):
    client_msg = str(msg)
    globalVariables.client.send(client_msg.encode())
    #print("Sending message")
    
    
def update_client_name_status(msg):
    nameStatusText.set(msg)
      
window.mainloop()
