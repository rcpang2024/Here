from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth as firebase_auth
from supabase import Client
from home.models import User
import jwt

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

class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        from django.conf import settings
        supabase = settings.SUPABASE_CLIENT
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        # Return None if no token is provided
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        id_token = auth_header.split('Bearer ')[1]

        try:
            decoded_token = supabase.auth.get_user(id_token)            
            identity_data = decoded_token.user.identities[0].identity_data
            email = identity_data['email']
            if not identity_data or "email" not in identity_data:
                raise AuthenticationFailed("Email not found in token identity data.")
            
            user = User.objects.get(email=email)
            user.is_authenticated = True
            return(user, id_token)
        except AttributeError as e:
            print(f"AttributeError: {str(e)}")
            raise AuthenticationFailed("Invalid token structure.")
        except User.DoesNotExist:
            print("User with the given email does not exist.")
            raise AuthenticationFailed("User not found.")
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            raise AuthenticationFailed(f"Authentication error: {str(e)}")
