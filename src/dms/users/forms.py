from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    """
