import tkinter as tk
import socket
import threading

import globalVariables

window = tk.Tk()
window.title("Server")

# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT, padx = 10)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

client_name = " "
clients = []
clients_names = []
clients_status = []


# Start server function
def start_server():
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    globalVariables.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print(socket.AF_INET)
    #print(socket.SOCK_STREAM)

    globalVariables.server.bind((globalVariables.HOST_ADDR, globalVariables.HOST_PORT))
    globalVariables.server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (globalVariables.server, " "))

    lblHost["text"] = "Host: " + globalVariables.HOST_ADDR
    lblPort["text"] = "Port: " + str(globalVariables.HOST_PORT)
    #print("start")

# Stop server function
def stop_server():
    #print("stop")

    global clients, clients_names, clients_status
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    
    clients_names = []
    clients_status = []
    update_client_names_display(clients_names, clients_status)  # update client names display    
    update_name_status_on_client_side(clients_names, clients_status, clients)
    
    for c in clients:
        msg = "BYE!"
        try:
            c.send(msg.encode())
            c.close()
        except:
           pass
           
    clients = []
    globalVariables.server.close()

def accept_clients(the_server, y):
    while True:
        try:
            client, addr = the_server.accept()
            clients.append(client)

            # use a thread so as not to clog the gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))
        except:
            break

# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global client_name, clients, clients_addr
    client_msg = " "

    # send welcome message to client
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
    client_connection.send(welcome_msg.encode())

    if client_name not in clients_names:
        clients_names.append(client_name)
        clients_status.append('Online')
    else:
        idx2 = clients_names.index(client_name)
        clients_status[idx2] = 'Online'
        clients[idx2] = clients[-1]
        clients.pop()
    
    update_client_names_display(clients_names, clients_status)  # update client names display
    
    update_name_status_on_client_side(clients_names, clients_status, clients)


    while True:
        try:
            data = client_connection.recv(4096).decode()
        except:
            break
        
        if not data: break
        #if data == "exit": break

        client_msg = data

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]
        

        for c in clients:
            if c != client_connection: # not itself
            
                #print("Recevied",client_msg)
                			    
                if client_msg=="exit":
                    server_msg = str(sending_client_name + " has left...")
                elif client_msg=="type_indicator_encode": # check type indicator
                    #print("Receive indicator")
                    server_msg = str(sending_client_name + " is typing...")
                elif client_msg=="type_indicator_release_encode":
                    #print("Receive indicator release")
                    server_msg = str("type_indicator_release_decode")
                else:
                    server_msg = str(sending_client_name + "->" + client_msg)
                
                try:
                    c.send(server_msg.encode())
                except:
                    pass
            else:
                if "status_encode" in client_msg: 
                    msg = client_msg.split("\n",1)[1]   
                    #print(msg)
                    idx3 = get_client_index(clients, client_connection)
                    clients_status[idx3] = msg
                    update_client_names_display(clients_names, clients_status)
                    update_name_status_on_client_side(clients_names, clients_status, clients)
                    
                        
                        
        if data == "exit": break

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    
    if idx >= 0 and len(clients_status)>0:
        clients_status[idx] = 'Offline'
        
        
    update_name_status_on_client_side(clients_names, clients_status, clients)
    
    server_msg = "BYE!"
    try:
        client_connection.send(server_msg.encode())
        client_connection.close()
    except:
        pass

    update_client_names_display(clients_names, clients_status)  # update client names display
    
    
# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    if len(client_list)==0:
        idx = -1
    
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list, status_list):
   tkDisplay.config(state=tk.NORMAL)
   tkDisplay.delete('1.0', tk.END)

   for c,s in zip(name_list, status_list):
       entry = c + " : " + s +"\n"
       tkDisplay.insert(tk.END, entry)
   tkDisplay.config(state=tk.DISABLED)
   display_content = tkDisplay.get('1.0', 'end-1c')
   return display_content

def update_name_status_on_client_side(name_list, status_list, clients):
    msg = "name_status_encode \n"
    for n, s in zip(name_list, status_list):
        msg = msg + n + " : " + s + "\n"

    for c in clients:
        try:
            c.send(msg.encode())
        except:
            #print(c, "is disconnected")
            pass
    
window.mainloop()