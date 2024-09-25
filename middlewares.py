import firebase_admin
from firebase_admin import auth
from django.http import JsonResponse

# Checks for authorization header containing ID token, verifies it with admin SDK and extracts user UID
class FirebaseTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            # Check if the token is a Bearer token
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
                try:
                    # Verify the ID token using Firebase Admin SDK
                    decoded_token = auth.verify_id_token(id_token)
                    request.user_id = decoded_token['uid']  # Set user ID to the request
                except Exception as e:
                    return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header not found'}, status=401)

        return self.get_response(request)