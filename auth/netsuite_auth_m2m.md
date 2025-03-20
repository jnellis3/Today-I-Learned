# Authenticating NetSuite with Python using Auth2.0 M2M Credentials

Lately I've been doing a lot of research into different authentication methods. Our company typically uses token based authentication for integrations, but we would like to move away from that in the future for more robust authentication. Today I learned how to authenticate with Netsuite using the Machine to Machine OAuth2.0 flow.

## Step 1: Create Integration Record

As always, the first step is to create the integration record to generate the CLIENT_ID and CLIENT_SECRET. Under the OAuth2.0 tab, we select Client Credentials (Machine To Machine) Grant as well as our requested scopes.

## Step 2: Create Certificates

The next step seemed confusing at first, but it ended up being much easier then our typical authentication methods. We need to generate a public/private key pair on our machine and upload the public key to NetSuite. I used openssl and executed the following command:

```bash
openssl req -new -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 365 -out public.pem -keyout private.pem 
```

This will generate a public.pem and private.pem file in the same directory that the command was executed under. There are a few options to go through when generating the key, but they are not required.

The public key then needs to be uploaded to NetSuite under setup --> Integration --> OAuth2.0 Client Credentials (M2M) Setup. Here we can select the entity and role that this key applies to. Once uploaded this will give us a certificate key, which will later be used as our KID variable in python.

## Step 3: Request Token

Now we are ready to request the token in Netsuite. The following variables for the previous steps will be required:

```python
ACCOUNT_ID = ""  # Replace with your account ID
CLIENT_ID = ""  # Replace with your actual client_id (consumer key)
PRIVATE_KEY_PATH = ""  # Path to your private key file
KID = ""  # Replace with the Key ID from your integration (example from JS snippet)

# The NetSuite token endpoint
TOKEN_URL = f"https://{ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token"

# Define scopes as per your integration setup.
# The JS snippet shows ["restlets","rest_webservices"] as an example.
SCOPES = ["restlets"]
```

The token generation endpoint takes a json web token as authentication, the below code generates this token and makes the request to the token endpoint:

```python
def generate_jwt(client_id, private_key, kid, audience, scopes):
    # Current timestamp
    iat = int(time.time())
    # Token is valid for 60 minutes
    exp = iat + 3600

    # JWT payload
    payload = {
        "iss": client_id,
        "scope": scopes,
        "iat": iat,
        "exp": exp,
        "aud": audience
    }

    # JWT header
    headers = {
        "alg": "ES256",  # As per the JS snippet
        "typ": "JWT",
        "kid": kid        # Key ID mapped in NetSuite
    }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token

def get_access_token(private_key_path, client_id, kid):
    # Load the private key
    with open(private_key_path, "r") as pk_file:
        private_key_data = pk_file.read()

    # Generate the JWT assertion
    jwt_assertion = generate_jwt(
        client_id=client_id,
        private_key=private_key_data,
        kid=kid,
        audience=TOKEN_URL,
        scopes=SCOPES
    )

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_assertion
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching token: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        token_response = get_access_token(PRIVATE_KEY_PATH, CLIENT_ID, KID)
        print(token_response)
    except Exception as e:
        print(f"Error: {e}")
```

This will print out our token! Now we can make requests to Netsuite by simply using this token as our Bearer token.