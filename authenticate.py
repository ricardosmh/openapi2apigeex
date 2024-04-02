import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

def generate_token():
    service_account_path = "service-accounts/service_account.json"
    try:
        credentials = service_account.Credentials.from_service_account_file(service_account_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except:
        print("An exception occurred")
        return False
    
    
if __name__ == "__main__":
    generate_token()