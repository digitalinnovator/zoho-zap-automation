# working code for second code by zapier in which we fetch/store/get token and also get contact detail.
# input data are 1).customer_id from looping step 2).estimate_id from looping step 3).access_token from storage 4). expiration_time from storage
import requests
import time

def get_access_token(refresh_token, client_id, client_secret):
    token_url = 'https://accounts.zoho.com/oauth/v2/token'
    params = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }

    response = requests.post(token_url, data=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch token: {response.text}")

    data = response.json()
    access_token = data['access_token']
    expiration_time = time.time() + data['expires_in'] - 300  # Renew 5 minutes before expiry

    return access_token, expiration_time

def fetch_contact_details(customer_id, access_token):
    base_url = f'https://www.zohoapis.com/invoice/v3/contacts/{customer_id}'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'X-com-zoho-invoice-organizationid': 'env.X-com-zoho-invoice-organizationid'
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code == 401:  # Token expired
        raise Exception("Access token expired")

    response.raise_for_status()  # Raise an error for other bad responses
    return response.json()

# Hard-coded credentials
refresh_token = 'env.refresh_token'
client_id = 'env.client_id'
client_secret = 'env.client_secret'

# Initialize output
output = {'contact_details': None, 'error': None, 'estimate_url': None, 'access_token': None, 'expiration_time': None}

try:
    # Ensure required inputs are present
    customer_id = input_data.get('customer_id')
    estimate_id = input_data.get('estimate_id')

    if not customer_id or not estimate_id:
        raise ValueError("Missing required input: 'customer_id' or 'estimate_id'")

    # Fetch the access token
    access_token, expiration_time = get_access_token(refresh_token, client_id, client_secret)

    # Store the access token and expiration time for the next step
    output['access_token'] = access_token
    output['expiration_time'] = expiration_time

    # Fetch contact details for the current customer_id
    contact_details = fetch_contact_details(customer_id, access_token)

    # Generate the estimate URL for the current estimate_id
    estimate_url = f"https://invoice.zoho.com/app#/quotes/{estimate_id}"

    # Assign results to output
    output['contact_details'] = contact_details
    output['estimate_url'] = estimate_url

except Exception as e:
    # Handle errors and add to output
    output['error'] = str(e)

# Return the final output for each iteration
return output

