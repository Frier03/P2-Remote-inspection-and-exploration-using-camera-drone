'''Contains the `middleware` function that implements authorization for the FastAPI application.

This module defines the `middleware` function that implements authorization for the FastAPI application. The function checks whether a user is authorized to access certain routes by checking for a valid access token in the request headers. 

The `routes_with_authorization` list defines the routes that require authorization. If the request URL does not match any of the routes in the list, the middleware function simply calls the route origin.

The `blacklisted_tokens` dictionary stores access tokens that have been invalidated due to logout or expiration. If a user logs out, the middleware function adds the token to the `blacklisted_tokens` dictionary with an expiration time of 24 hours. The `is_user_authorized` function is imported from the `helper_functions` module and checks whether the access token is valid and belongs to an authorized user.
    
Attributes:
    routes_with_authorization (list): A list of route paths that require authorization.
    blacklisted_tokens (dict): A dictionary that stores invalidated access tokens.
'''

# FastAPI
from fastapi import Request
from datetime import datetime, timedelta

# Starlette. We cannot `raise HTTPException` because FastAPI does not support middleware exceptions.
from starlette.responses import HTMLResponse as starletteHTMLResponse 

# Own function to validate if a user is authorized.
from helper_functions import is_user_authorized

# Routes that have authorization.
routes_with_authorization: list = [ # TODO: Add all routes that is sensitive + docs
    "/v1/api/frontend/protected", 
    "/v1/api/frontend/logout",
    "/v1/api/frontend/users/me",
    "/v1/api/frontend/relayboxes/all",
    "/v1/api/frontend/drone/takeoff",
    "/v1/api/frontend/drone/land",
    "/v1/api/frontend/drone/new_command",
    "/v1/api/relay/heartbeat", 
    "/v1/api/relay/relayboxes/all"
]

# Dictionary that stores invalidated access tokens
blacklisted_tokens: dict[int: str] = {}

async def middleware(request: Request, call_next):
    """Handle user authorization for protected routes.

    This function checks the access token in the request headers for routes that require authorization, 
    to ensure that the user has the required permissions. It also blacklists access tokens for logged out users.

    Args:
        request (Request): The incoming request.
        call_next (function): The next function to call in the FastAPI pipeline.

    Returns:
        Any: The response from the FastAPI pipeline.
    """
       
    # Routes with no authentication.
    if request.url.path not in routes_with_authorization:
        return await call_next(request)
    
    # Get access token from headers.
    access_token: str | None = request.headers.get('authorization')

    # If no access token declared.
    if access_token is None:
        return starletteHTMLResponse(status_code=401)
    
    # Try split "Bearer" from access token. Bearer is a type of authorization header in HTML.
    try:
        access_token: str = access_token.split("Bearer ")[1]

    # If access token is not formatted correctly.
    except (ValueError, IndexError): 
        return starletteHTMLResponse(status_code=400)

    # Is access token blacklisted?
    if access_token in blacklisted_tokens.values():
        return starletteHTMLResponse(status_code=401)

    # Is user not authorized with this access token.
    if not is_user_authorized(access_token, blacklisted_tokens):
        return starletteHTMLResponse(status_code=401)
    
    # Call route origin and await response.
    response = await call_next(request)

    # If a user tries to logout. Then force expire the access token by storing it in blacklisted tokens
    if request.url.path == "/v1/api/frontend/logout":

        # Create expiration date of 24 hours for the blacklisted access token
        expire: datetime = datetime.utcnow() + timedelta(minutes=24*60) # Output example: '2022-11-28T16:42:17Z'
        expire: int = int(expire.timestamp()) # Convert '2022-11-28T16:42:17Z' to seconds (integer) since 1st Jan 1970.

        # Store the token and expiration in blacklisted tokens.
        blacklisted_tokens[expire]: dict[int, str] = access_token

    # Return response
    return response