import firebase_admin
from firebase_admin import auth
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

# Checks for authorization header containing ID token, verifies it with admin SDK and extracts user UID
class FirebaseTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
                try:
                    # Verify the ID token
                    decoded_token = auth.verify_id_token(id_token)
                    request.user_id = decoded_token['uid']
                except auth.ExpiredIdTokenError:
                    raise PermissionDenied("Expired token")
                except auth.InvalidIdTokenError:
                    raise PermissionDenied("Invalid token")
                except Exception as e:
                    raise PermissionDenied(f"Token verification failed: {e}")
        else:
            request.user_id = None  # Unauthenticated request

        return self.get_response(request)