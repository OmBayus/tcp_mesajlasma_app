import socket
import threading
import json
import os


# client
class ChatClient:
    def __init__(self, username, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.username = username
        self.gruplar = [{
            'title':'Genel',
            'kisiler':[]
        }]
        self.users = dict()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.send_username()

    # kullanıcı adını göndermek için
    def send_username(self):
        msg_data = {'username': self.username, 'command': 'add_user'}
        self.client.send(json.dumps(msg_data).encode('utf-8'))


    # mesaj göndermek için
    def send_message(self, message, target_username):
        msg_data = {'username': self.username, 'message': message, 'target_username': target_username,'command': 'msg'}
        self.client.send(json.dumps(msg_data).encode('utf-8'))
    
    # kullanıcı listesini görmek için
    def kullanicilari_listele(self):
        msg_data = {'username': self.username, 'command': 'list_users'}
        self.client.send(json.dumps(msg_data).encode('utf-8'))

    # gelen mesajları dinlenir
    def listen_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                message = json.loads(message)
                if message['command'] == 'add_user':
                    if message['status'] == 'OK':
                        sub_main(self)
                        continue
                    else:
                        print("Kullanıcı adı zaten kullanılıyor")
                        self.username = input("Kullanıcı adı: ")
                        self.send_username()
                        continue
                elif message['command'] == "list_users":
                    os.system('clear')
                    print("0.Geri")
                    for i in range(len(message["users"])):
                        print(f"{i+1}. {message['users'][i]}")
                    secim = input("Seçiminiz: ")
                    if secim == '0':
                        sub_main(self)
                        continue
                    print("0.Geri")
                    print("1.Gruba Ekle")
                    print("2.Mesajları Görüntüle")
                    print("3.Mesaj Gönder")
                    secim2 = input("Seçiminiz: ")
                    if secim2 == '1':
                        t_user = message["users"][int(secim)-1] 
                        print("Gruplar")
                        print("0.Geri")
                        for i in range(len(self.gruplar)):
                            print(f"{i+1}. {self.gruplar[i]['title']}")
                        grup_secim = input("Grub seçiniz: ")
                        if grup_secim == '0':
                            sub_main(self)
                            continue
                        grup = self.gruplar[int(grup_secim)-1]
                        if t_user not in grup['kisiler']:
                            grup['kisiler'].append(t_user)
                    elif secim2 == '2':
                        print(message["users"][i],"Son 5 Mesajı")
                        t_user = message["users"][int(secim)-1] 
                        # last 5 messages
                        if t_user in self.users:
                            for mes in self.users[t_user]['messages'][-5:]:
                                if mes['is_me']:
                                    print(f"{self.username}: {mes['message']}")
                                else:
                                    print(f"{t_user}: {mes['message']}")
                        else:
                            print("Mesaj yok")
                        filtre = input("Geçmiş Mesajlar Arasından Ara:")
                        print(f"Bulunan Mesajlar")
                        for mes in self.users[t_user]['messages']:
                            if filtre in mes['message']:
                                if mes['is_me']:
                                    print(f"{self.username}: {mes['message']}")
                                else:
                                    print(f"{t_user}: {mes['message']}")
                        input("Devam etmek için bir tuşa basınız")
                    elif secim2 == '3':
                        t_user = message["users"][int(secim)-1] 
                        mesaj = input("Mesajınız: ")
                        self.send_message(mesaj, t_user)
                        msg = {
                            'message':mesaj,
                            'is_me':True
                        }
                        
                        if t_user not in self.users:
                            self.users[t_user] = {
                                'messages':[]
                            }
                            self.users[t_user]['messages'].append(msg)
                        else:
                            self.users[t_user]['messages'].append(msg)
                    else:
                        continue
                elif message['command'] == "message":
                    msg = { 
                        'message':message['message'],
                        'is_me':False
                    }
                    
                    if message['sender'] not in self.users:
                        self.users[message['sender']] = {
                            'messages':[]
                        }
                        self.users[message['sender']]['messages'].append(msg)
                    else:
                        self.users[message['sender']]['messages'].append(msg)
                    print(self.users)
                    continue
                sub_main(self)



                    
            except Exception as e:
                print("Error",e)
                self.client.close()
                break

    def start(self):
        thread = threading.Thread(target=self.listen_messages)
        thread.start()


def main():
    username = input("Kullanıcı adınızı giriniz: ")
    client = ChatClient(username,host='localhost', port=12345)
    client.start()

def sub_main(client):
    os.system('clear')
    print("0.Çıkış")
    print("1.Kullanıcıları Listele")
    print("2.Gruplar")
    secim = input("Seçiminiz: ")
    if secim == '1':
        os.system('clear')
        client.kullanicilari_listele()
        return
    elif secim == '2':
        os.system('clear')
        print("Gruplar")
        print("0.Geri")
        print("1.Grup Oluştur")
        print("2.Grup Seç")
        secim = input("Seçiminiz: ")
        if secim == '0':
            pass
        elif secim == '1':
            print("Grup Oluştur")
            grup_adi = input("Grup adı: ")
            client.gruplar.append({
                'title':grup_adi, 
                'kisiler':[]
            })
        elif secim == '2':
            print("Gruplar")
            print("0.Geri")
            for i in range(len(client.gruplar)):
                print(f"{i+1}. {client.gruplar[i]['title']}")
            secim2 = input("Seçiminiz: ")
            if secim2 == '0':
                pass
            else:
                secili_grup = client.gruplar[int(secim2)-1]
                if len(secili_grup['kisiler']) == 0:
                    print("Grup boş")
                else:
                    print("Grup:", secili_grup["title"])
                    print("0.Geri")
                    for i in range(len(secili_grup['kisiler'])):
                        print(f"{i+1}. {secili_grup['kisiler'][i]}")
                    secim3 = input("Seçiminiz: ")
                    if secim3 == '0':
                        pass
                    elif int(secim3) > len(secili_grup['kisiler']):
                        print("Hatalı seçim")
                    else:
                        t_user = secili_grup['kisiler'][int(secim3)-1]
                        print("0.Geri")
                        print("1.Mesaj Gönder")
                        print("2.Mesajları Görüntüle")
                        secim4 = input("Seçiminiz: ")
                        if secim4 == '0':
                            pass
                        elif secim4 == '1':
                            inp = input("Mesajınız:")
                            msg = {
                                'message':inp,
                                'is_me':True
                            }
                            print("t_user",t_user)
                            client.send_message(inp, t_user)
                            if t_user not in client.users:
                                client.users[t_user] = {
                                    'messages':[]
                                }
                                client.users[t_user]['messages'].append(msg)
                            else:
                                client.users[t_user]['messages'].append(msg)
                        elif secim4 == '2':
                            print(t_user,"Son 5 Mesajı")
                            if t_user in client.users:
                                for mes in client.users[t_user]['messages'][-5:]:
                                    if mes['is_me']:
                                        print(f"{client.username}: {mes['message']}")
                                    else:
                                        print(f"{t_user}: {mes['message']}")
                            else :
                                print("Mesaj yok")
                            filtre = input("Geçmiş Mesajlar Arasından Ara:")
                            print(f"Bulunan Mesajlar")
                            for mes in client.users[t_user]['messages']:
                                if filtre in mes['message']:
                                    if mes['is_me']:
                                        print(f"{client.username}: {mes['message']}")
                                    else:
                                        print(f"{t_user}: {mes['message']}")
                            input("Devam etmek için bir tuşa basınız")
                        else:
                            pass
        sub_main(client)

main()