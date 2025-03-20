# Implementing OAuth2.0 Flow

The following snippit taken from a test project to authenticate an Excel plugin with OAuth.

```python
from datasette import hookimpl, Response
from urllib.parse import urlencode
import baseconv
import httpx
import secrets
import time
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import requests

REDIRECT_URI = "https://simplecell.gvoserver1.com/-/auth0-callback"

async def auth0_login(request, datasette):

    try:
        config = _config(datasette)
    except ConfigError as e:
        return _error(datasette, request, str(e))

    state = secrets.token_hex(16)
    url = "https://{}/authorize?".format(config["domain"]) + urlencode(
        {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": REDIRECT_URI,
            "scope": config.get("scope") or "openid profile email",
            "state": state,
        }
    )

    response = Response.redirect(url)
    response.set_cookie("auth0-state", state, max_age=3600)
    return response


async def auth0_callback(request, datasette):

    try:
        config = _config(datasette)
    except ConfigError as e:
        return _error(datasette, request, str(e))

    code = request.args["code"]
    state = request.args.get("state") or ""

    # Compare state to their cookie
    expected_state = request.cookies.get("auth0-state") or ""
    if not state or not secrets.compare_digest(state, expected_state):
        return _error(
            datasette,
            request,
            "state check failed, your authentication request is no longer valid",
        )

    # Exchange the code for an access token
    response = httpx.post(
        "https://{}/oauth/token".format(config["domain"]),
        data={
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
        auth=(config["client_id"], config["client_secret"]),
    )

    if response.status_code != 200:
        return _error(
            datasette,
            request,
            "Could not obtain access token: {}".format(response.status_code),
        )

    # This should have returned an access token
    access_token = response.json()["access_token"]

    # Exchange that for the user info
    profile_response = httpx.get(
        "https://{}/userinfo".format(config["domain"]),
        headers={"authorization": "Bearer " + access_token},
    )
    if profile_response.status_code != 200:
        return _error(
            datasette,
            request,
            "Could not obtain user info: {}".format(profile_response.status_code),
        )

    id_token = response.json()["id_token"]
    redirect_response = Response.redirect(f"/setup#access_token={id_token}")
    expires_at = int(time.time()) + 3600

    redirect_response.set_cookie(
        "ds_actor",
        datasette.sign(
            {
                "a": profile_response.json(),
                "e": baseconv.base62.encode(expires_at)
            },
            "actor"
        )
    )
    return (redirect_response)

@hookimpl
async def actor_from_request(request, datasette):

    try:
        config = _config(datasette)
    except ConfigError as e:
        return _error(datasette, request, str(e))

    id_token = request.headers.get("authorization") or ""
    if not id_token.startswith("Bearer "):
        return None
    id_token = id_token.split("Bearer ")[1]

    # Fetch jwks
    jwks_response = requests.get(f"https://{config['domain']}/.well-known/jwks.json")
    jwks_response.raise_for_status()
    jwks = jwks_response.json()

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header["kid"]

    public_key = None
    for key in jwks["keys"]:
        if key["kid"] == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break

    if not public_key:
        return None

    try:
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=config["client_id"],
            issuer=f"https://{config['domain']}/"
        )
        return decoded_token
    except:
        return None



@hookimpl
def register_routes():
    return [
        (r"^/-/auth0-login$", auth0_login),
        (r"^/-/auth0-callback$", auth0_callback)
    ]


class ConfigError(Exception):
    pass


def _config(datasette):
    config = datasette.plugin_config("datasette-auth0")
    missing = [
        key for key in ("domain", "client_id", "client_secret") if not config.get(key)
    ]
    if missing:
        raise ConfigError(
            "The following auth0 plugin settings are missing: {}".format(
                ", ".join(missing)
            )
        )
    return config


def _error(datasette, request, message):
    datasette.add_message(request, message, datasette.ERROR)
    return Response.redirect("/")


@hookimpl
def menu_links(datasette, actor):
    if not actor:
        return [
            {
                "href": datasette.urls.path("/-/auth0-login"),
                "label": "Sign in with Auth0",
            },
        ]
```