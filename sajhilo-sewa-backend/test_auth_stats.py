import urllib.request
import urllib.parse
import json

base_url = 'http://localhost:8000'

def login():
    data = urllib.parse.urlencode({'username': 'test1@example.com', 'password': 'password123'}).encode('ascii')
    req = urllib.request.Request(f'{base_url}/auth/login', data=data)
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())
            return res.get('access_token')
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def get_stats(token):
    req = urllib.request.Request(f'{base_url}/admin/stats/')
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Stats fetch failed: {e}")
        return None

if __name__ == "__main__":
    token = login()
    if token:
        stats = get_stats(token)
        print(f"Stats: {stats}")
    else:
        print("Could not get token. Testing registration endpoint first...")
        
        # Try registering test1@example.com
        reg_data = json.dumps({
            "username": "testuser",
            "email": "test1@example.com",
            "password": "password123"
        }).encode('utf-8')
        
        req = urllib.request.Request(f'{base_url}/auth/register', data=reg_data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                 print("Registered successfully.")
                 token = login()
                 if token:
                     print(f"Stats: {get_stats(token)}")
        except Exception as e:
             print(f"Registration failed (might already exist): {e}")
