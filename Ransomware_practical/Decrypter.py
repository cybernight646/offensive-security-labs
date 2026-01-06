from cryptography.fernet import Fernet
import os
import time
import concurrent.futures

class Decryptor:
    def __init__(self):
        self.sysRoot = os.path.expanduser('~')
        self.key = None
        self.crypter = None
        self.file_exts = ['png', 'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'mp3', 'mp4', 'avi', 'wav', 'mov', 'zip', 'rar', 'html', 'css', 'js', 'py', 'java', 'cpp']  # Specify the file extensions to decrypt

    def read_key_from_file(self):
        # Read the key from PUT_ME_ON_DESKTOP.txt
        try:
            with open(os.path.join(self.sysRoot, 'Desktop', 'PUT_ME_ON_DESKTOP.txt'), 'r') as f:
                self.key = f.read()
                self.crypter = Fernet(self.key)
                print("Key read successfully.")
                return True
        except FileNotFoundError:
            print("PUT_ME_ON_DESKTOP.txt not found.")
            return False

    def decrypt_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.crypter.decrypt(encrypted_data)
            with open(file_path, 'wb') as f:
                f.write(decrypted_data)
            print(f"Decrypted: {file_path}")
        except Exception as e:
            print(f"Error decrypting {file_path}: {e}")

    def decrypt_files(self):
        if self.key is None or self.crypter is None:
            print("Key is missing. Aborting decryption.")
            return

        print("Decrypting files...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            files_to_decrypt = []
            for root, dirs, files in os.walk(self.sysRoot):
                for file in files:
                    if file.split('.')[-1] in self.file_exts:
                        files_to_decrypt.append(os.path.join(root, file))
            executor.map(self.decrypt_file, files_to_decrypt)

    def start(self):
        while True:
            if self.read_key_from_file():
                self.decrypt_files()
                break  # Stop listening once decryption is done
            time.sleep(10)  # Check for PUT_ME_ON_DESKTOP.txt every 10 seconds

if __name__ == "__main__":
    decryptor = Decryptor()
    decryptor.start()
