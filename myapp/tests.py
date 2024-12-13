from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

class LoginViewTests(TestCase):
    
    def setUp(self):
        """Create a test user before each test"""
        self.username = 'testuser'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, email='testuser@example.com', password=self.password)

    def test_login_page_loads(self):
        """Test that the login page loads successfully"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_redirects_authenticated_user(self):
        """Test that an authenticated user is redirected to the dashboard"""
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('login'))  # Try to access the login page while logged in
        self.assertRedirects(response, reverse('dashboard'))  # Should be redirected to dashboard

    def test_successful_login_with_valid_credentials(self):
        """Test that a user can log in with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username_or_email': self.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('dashboard'))  # Should redirect to dashboard after successful login

    def test_unsuccessful_login_with_invalid_username_or_email(self):
        """Test that a user cannot log in with an invalid username or email"""
    # Attempt to log in with an invalid username or email
        response = self.client.post(reverse('login'), {
        'username_or_email': 'invalidusername@example.com',  # Invalid email or username
        'password': 'password123'  # Correct password (but wrong username/email)
        })

    # Check that the response is a redirect back to the login page (302)
        self.assertEqual(response.status_code, 302)  # Expecting a 302 redirect
    
    # Follow the redirect to the login page to check for the error message
        response = self.client.get(reverse('login'))  # Follow the redirect to the login page

    # Retrieve messages from the response
        messages = list(get_messages(response.wsgi_request))

    # Ensure that the error message is present
        self.assertEqual(str(messages[0]), 'Invalid username/email or password.')

