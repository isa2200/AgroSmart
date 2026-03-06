import MySQLdb
import os

def check_connection(user, password, port=3306):
    try:
        db = MySQLdb.connect(host="localhost", user=user, passwd=password, port=port)
        print(f"SUCCESS: User='{user}', Password='{password}', Port={port}")
        db.close()
        return True
    except Exception as e:
        # print(f"FAILED: User='{user}', Password='{password}', Port={port} - Error: {e}")
        return False

users = ['root', 'agrosmart_user', 'agrosmart', 'admin']
passwords = ['', 'root', 'admin', 'password', '123456', '12345678', 'agrosmart_pass', 'super_root_password', 'mysql']

print("Checking database connection...")

found = False
for user in users:
    for pwd in passwords:
        if check_connection(user, pwd):
            found = True
            break
    if found:
        break

if not found:
    print("No valid credentials found.")
