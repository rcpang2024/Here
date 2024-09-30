import firebase_admin
from firebase_admin import auth
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

# Checks for authorization header containing ID token, verifies it with admin SDK and extracts user UID
class FirebaseTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print("Authorization Header: ", request.headers.get('HTTP_AUTHORIZATION'))
        # print("Request method: ", request.method)
        # return self.get_response(request)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
                print("id_token: ", id_token)
                try:
                    decoded_token = auth.verify_id_token(id_token)
                    print("decoded_token: ", decoded_token)
                    request.user_id = decoded_token['uid']  # Attach user ID to request
                    print(f"Middleware: user_id is {request.user_id}")
                except auth.ExpiredIdTokenError:
                    print("Expired")
                    return JsonResponse({'error': 'Expired token'}, status=401)
                    # raise PermissionDenied("Expired token")
                except auth.InvalidIdTokenError:
                    print("Invalid")
                    return JsonResponse({'error': 'Invalid token'}, status=401)
                    # raise PermissionDenied("Invalid token")
                except Exception as e:
                    return JsonResponse({'error': 'Exception'}, status=401)
                    # raise PermissionDenied(f"Token verification failed: {e}")
        else:
            print("in else")
            request.user_id = None  # Unauthenticated request
        print("self", self.get_response(request))
        return self.get_response(request)
