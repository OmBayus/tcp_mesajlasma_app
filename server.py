import socket
import threading
import json


# server
class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = {}  # Kullanıcı adını ve bağlantıyı saklamak için

    def handle_client(self, client, addr):
        username = None
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                # dict olarak gelen mesajı parse ediyoruz
                msg_data = json.loads(message)
                username = msg_data['username']
                # add_user komutu, sisteme kullanıcı eklemek için 
                if msg_data['command'] == 'add_user':
                    if username in self.clients:
                        client.send(json.dumps({'command': 'add_user', 'status': 'FAIL'}).encode('utf-8')) # kullanıcı adı zaten varsa
                        print(f"{username} zaten bağlı.")
                    else:
                        self.clients[username] = {'connection': client, 'groups': []}
                        print(f"{username} bağlandı.")
                        client.send(json.dumps({'command': 'add_user', 'status': 'OK'}).encode('utf-8'))
                else: # add_user dışındaki mesajlar, mesaj işleme fonksiyonuna gönderiliyor
                    self.process_message(client, msg_data)
            except Exception as e:
                print(f"Error: {e}")
                client.close()
                if username:
                    del self.clients[username]
                    print(f"{username} bağlantı listesinden çıkarıldı.")
                break

    def process_message(self, client, msg_data):
        username = msg_data['username']
        message = msg_data.get('message', None)
        target_username = msg_data.get('target_username', None)
        command = msg_data.get('command', None)

        print(msg_data)

        # sisteme giriş yapan kullanıcılar, bu komut ile diğer kullanıcıları görebilir
        if command == "list_users":
            self.send_user_list(username)
            return
        # mesaj göndermek için
        if command == 'msg':
            self.send_to_user(message, target_username,username)
            return
            

    # yalnız bir clienta mesaj göndermek için
    def send_to_user(self, message, target_username,sender):
        if target_username in self.clients:
            answer = {'command': 'message', 'message': message,'sender':sender}
            target_client = self.clients[target_username]['connection']
            target_client.send(json.dumps(answer).encode('utf-8'))
        else:
            print(f"Kullanıcı {target_username} bulunamadı.")
    
    # sisteme giriş yapan kullanıcılar, bu komut ile diğer kullanıcıları görebilir
    def send_user_list(self, username):
        user_list = list(self.clients.keys())
        user_list.remove(username)
        answer = {'command': 'list_users', 'users': user_list}
        target_client = self.clients[username]['connection']
        target_client.send(json.dumps(answer).encode('utf-8'))


    def start(self):
        print("Server başlatıldı...")
        while True:
            client, addr = self.server.accept()
            # print(f"{addr} bağlandı.")
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.start()


def main():
    server = ChatServer(host='localhost', port=12345)
    server.start()


main()