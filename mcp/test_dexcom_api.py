import requests
import json
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')

DEXCOM_API_URL = 'https://sandbox-api.dexcom.com'
DEXCOM_CLIENT = os.getenv('DEXCOM_CLIENT')
DEXCOM_CLIENT_SECRET = os.getenv('DEXCOM_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def get_auth_url():
    """1. Generates the URL for Dexcom login and authorization."""
    auth_url = (
        f"{DEXCOM_API_URL}/v2/oauth2/login?"
        f"client_id={DEXCOM_CLIENT}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=offline_access"
    )
    return auth_url

def get_access_token(code):
    """3. Exchanges the received 'code' for an 'access_token'."""
    token_url = f'{DEXCOM_API_URL}/v2/oauth2/token'
    data = {
        'client_id': DEXCOM_CLIENT,
        'client_secret': DEXCOM_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        print("\n--- 2. Exchanging for access token... ---")
        response = requests.post(token_url, data=data)
        response.raise_for_status() # Raise an exception if there's an error
        
        tokens = response.json()
        access_token = tokens['access_token']
        print("Successfully received access token.")
        return access_token
    
    except requests.exceptions.RequestException as e:
        print(f"\nFailed to exchange token.")
        print(f"Error: {e}")
        print(f"Server response: {response.text}")
        return None

def get_glucose_data(access_token):
    """4. Fetches glucose data using the 'access_token'."""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Fixed date for querying sandbox data
    glucose_url = f'{DEXCOM_API_URL}/v3/users/self/egvs'
    params = {
        'startDate': '2024-01-01T00:00:00',
        'endDate': '2024-01-02T00:00:00'
    }

    try:
        print("\n--- 3. Fetching glucose data... ---")
        response = requests.get(glucose_url, headers=headers, params=params)
        response.raise_for_status()
        
        glucose_data = response.json()
        print("Successfully fetched data.")
        return glucose_data
        
    except requests.exceptions.RequestException as e:
        print(f"\nFailed to fetch data.")
        if response.status_code == 401:
            print("Error: 401 Unauthorized (Token may be expired or invalid.)")
        else:
            print(f"Error: {e}")
        print(f"Server response: {response.text}")
        return None

def main():
    # 0. Check if required libraries are installed
    try:
        import requests
    except ImportError:
        print(" 'requests' library is required. Please run: pip install requests")
        return

    # 1. Generate and print the authorization URL
    auth_url = get_auth_url()
    print("--- 1. Start Dexcom Authorization ---")
    print("Copy the URL below and open it in your web browser:")
    print("\n" + auth_url + "\n")
    print("After logging in, you might see an error page like 'This site can’t be reached'. (This is normal)")
    print("Copy the **entire address (URL)** from that page and paste it below:")
    
    # 2. Get the callback URL from the user
    callback_url = input("\nPaste URL here: ")
    
    # Parse the 'code' from the input URL
    try:
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            print("\nCould not find 'code' in the URL. Please check if you copied the address correctly.")
            return
            
        code = query_params['code'][0]
        print("\nSuccessfully extracted authorization code.")
    
    except Exception as e:
        print(f"\nError parsing URL: {e}")
        return

    # 3. Get 'access_token' with the 'code'
    token = get_access_token(code)
    
    if token:
        # 4. Fetch data with the 'access_token'
        data = get_glucose_data(token)
        
        if data:
            # 5. Print the result (JSON)
            print("\n--- 4. Final Result (JSON) ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()