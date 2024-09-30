from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth as firebase_auth
from home.models import User

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Return None if no authentication header is provided

        id_token = auth_header.split('Bearer ')[1]
        try:
            # Verify the Firebase ID token
            decoded_token = firebase_auth.verify_id_token(id_token)
            print("decoded_token: ", decoded_token)
            email = decoded_token['email']
            user = User.objects.get(email=email)
            user.is_authenticated = True
            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(f'Invalid or expired token: {str(e)}')

