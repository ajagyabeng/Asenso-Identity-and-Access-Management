import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get('Authorization')
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        abort(403)
    return True


def verify_decode_jwt(token):
    """decodes and verifies the token provided"""
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())  # JSON Web Key Set(jwks)
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:  # 'kid' is The unique identifier for the key.
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
                # 'kty' The family of cryptographic algorithms used with the key.
                # 'use' How the key was meant to be used; sig represents the signature.
                # 'n' The modulus for the RSA public key.(https://www.rfc-editor.org/rfc/rfc7518#page-30)
                # 'e' The exponent for the RSA public key.(https://www.rfc-editor.org/rfc/rfc7518#page-30)
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        """a decorator that takes a token, verifies it, and returns a payload"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
