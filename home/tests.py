from django.test import TestCase
from .models import User, Event

# Create your tests here.
class UserTestCase(TestCase):
    def test_new_user_followers(self):
        user = User.objects.create(username='testuser', name='Test User', email='test@example.com', phone_number='1234567890')
        
        # Create some followers for the user
        follower1 = User.objects.create(username='follower1', name='Follower 1', email='follower1@example.com', phone_number='1111111111')
        follower2 = User.objects.create(username='follower2', name='Follower 2', email='follower2@example.com', phone_number='2222222222')
        follower3 = User.objects.create(username='follower3', name='Follower 3', email='follower3@example.com', phone_number='3333333333')
        
        # Add the followers to the new user's list_of_followers
        user.list_of_followers.add(follower1)
        user.list_of_followers.add(follower2)
        user.list_of_followers.add(follower3)
        user.save()
        
        # Check if the followers are correctly added to the followers' list_of_following
        follower1.refresh_from_db()
        follower2.refresh_from_db()

        self.assertTrue(user.list_of_followers.contains(follower3))

class EventTestCase(TestCase):
    def test_events(self):
        user = User.objects.create(username='testuser', name='Test User', email='test@example.com', phone_number='1234567890',
                                   user_type='organization')
        #user.save()
        event1 = Event.objects.create(id=0, creation_user=user, event_name="Watch party", location='Test Location', 
                                      date='2023-05-31 12:00:00')
        event2 = Event.objects.create(id=1, creation_user=user, event_name="Soccer", location='UNC', 
                                      date='2023-05-31 12:00:00')
        
        # Create some followers for the user
        follower1 = User.objects.create(username='follower1', name='Follower 1', email='follower1@example.com', phone_number='1111111111')
        follower2 = User.objects.create(username='follower2', name='Follower 2', email='follower2@example.com', phone_number='2222222222')
        follower3 = User.objects.create(username='follower3', name='Follower 3', email='follower3@example.com', phone_number='3333333333')
        
        event1.list_of_attendees.add(follower1)
        event1.list_of_attendees.add(follower2)
        event1.save()
        
        # Add the followers to the new user's list_of_followers
        user.list_of_followers.add(follower1)
        user.list_of_followers.add(follower2)
        user.list_of_followers.add(follower3)
        user.created_events.add(event1)
        user.created_events.add(event2)
        user.full_clean()

        self.assertIn(event1, user.created_events.all())
        self.assertIn(event2, user.created_events.all())
        for event in user.created_events.all():
            print(event.event_name)