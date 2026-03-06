
import requests

url = 'http://127.0.0.1:8000/usuarios/login/'

# Use a session to get CSRF token
s = requests.Session()
r = s.get(url)

try:
    csrftoken = s.cookies['csrftoken']
    print(f"CSRF Token: {csrftoken}")
    
    data = {
        'username': 'IsabelCGJ',
        'password': '123456789L',
        'csrfmiddlewaretoken': csrftoken
    }
    
    headers = {
        'Referer': url,
        'X-CSRFToken': csrftoken
    }
    
    print(f"Sending POST to {url} with username={data['username']}")
    r = s.post(url, data=data, headers=headers)
    
    print(f"Status Code: {r.status_code}")
    if "Usuario o contraseña incorrectos" in r.text:
        print("Found error message in response.")
    elif "Por favor, introduzca un nombre de usuario y clave correctos" in r.text:
        print("Found AuthenticationForm error message.")
    else:
        print("No error message found (or different one).")
        # print(r.text[:500])

except Exception as e:
    print(f"Error: {e}")
