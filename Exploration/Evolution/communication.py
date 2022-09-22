import socket
import threading

PORT = 45350

#HOST = "127.0.0.1"  # Standard loopback interface address (localhost)


def socket_send(ip, data_str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, PORT))
        s.sendall(str.encode(data_str))#b"Hello, world"
        #print("client sent", data_str)
        data = s.recv(1024)
        data = data.decode('utf-8')  # to str
        #print("client received", data)
    return data#response


class Socket_Listener:

    def __init__(self, start_listening=True, message_handler_func=None):# example: handle_message(data_str)=>answer_str
        if message_handler_func is not None:
            self.message_handler_func = message_handler_func
        else:
            self.message_handler_func = self.handle_message
        if start_listening:
            self.start()

    def handle_message(self, data):
        return "None"

    def _listen(self):
        #try:
        if True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#
                s.bind(("0.0.0.0", PORT))#socket.gethostname()
                s.listen()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            data = data.decode('utf-8')  # to str
                            print('received', data)

                            response_str=self.message_handler_func(data)

                            print('send', response_str)
                            conn.sendall(str.encode(response_str))
        #except:
        #    print('socket can not be initialized')

    def start(self):
        self.t=threading.Thread(target=self._listen, args=())
        self.t.start()



#sl = Socket_Listener()
#print(socket_send("localhost", "insert\r\n{'a':4, 'b':6, 'c':1}\r\n{'a':6, 'b':6, 'c':6}"))

