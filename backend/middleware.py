from fastapi import Request
from datetime import datetime, timedelta
from fastapi import Request

from starlette.responses import HTMLResponse as starletteHTMLResponse 
from helper_functions import is_user_authorized

routes_with_authorization = [
    "/v1/api/frontend/protected",
    "/v1/api/frontend/logout",
    "/v1/api/relay/heartbeat"
]

blacklisted_tokens = {}

async def middleware(request: Request, call_next):
    # Routes with no authentication
    if request.url.path not in routes_with_authorization: # Routes with no authentication
        return await call_next(request)
    
    # Get access token from headers
    access_token = request.headers.get('authorization')

    # If no access_token declared, raise 401
    if access_token is None:
        return starletteHTMLResponse(status_code=401)
    
    # Try split "Bearer" from access_token
    try:
        access_token = access_token.split("Bearer ")[1]
    except (ValueError, IndexError): # If token is not formatted correctly
        return starletteHTMLResponse(status_code=400)

    # Is token blacklisted?
    if access_token in blacklisted_tokens.values():
        return starletteHTMLResponse(status_code=401)

    # Is user not authorized with this access token
    if not is_user_authorized(access_token, blacklisted_tokens):
        return starletteHTMLResponse(status_code=401)
    
    # Await endpoint
    response = await call_next(request)
    if request.url.path == "/v1/api/frontend/logout":

        # Create expiration date of 24 hours
        expire = datetime.utcnow() + timedelta(minutes=24*60)
        expire = expire.timestamp()
    
        # Store token and expiration in blacklisted_tokens
        blacklisted_tokens[expire] = access_token

    return response