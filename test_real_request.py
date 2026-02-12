import urllib.request
import urllib.parse
import json

url = "http://127.0.0.1:8000/usuarios/login/"
data = urllib.parse.urlencode({
    'username': 'IsabelCGJ',
    'password': '123456789L.',
    'csrfmiddlewaretoken': 'dummy' # This might fail CSRF, but we want to see if it hits the server logs
}).encode('utf-8')

req = urllib.request.Request(url, data=data)
# We need to handle CSRF, so first GET to get the cookie
try:
    jar = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(jar)
    
    # 1. GET to set cookies
    print("Sending GET request...")
    response = opener.open(url)
    print(f"GET Status: {response.getcode()}")
    
    # Extract CSRF token from cookies (simple search in jar)
    csrf_token = ""
    for cookie in jar.cookiejar:
        if cookie.name == 'csrftoken':
            csrf_token = cookie.value
            break
            
    print(f"CSRF Token: {csrf_token}")
    
    # 2. POST with token
    data = urllib.parse.urlencode({
        'username': 'IsabelCGJ',
        'password': '123456789L.',
        'csrfmiddlewaretoken': csrf_token
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Referer', url)
    
    print("Sending POST request...")
    response = opener.open(req)
    print(f"POST Status: {response.getcode()}")
    print(f"Final URL: {response.geturl()}") # Should be redirected
    
except Exception as e:
    print(f"Error: {e}")
