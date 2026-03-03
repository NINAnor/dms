from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin


class FeideSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin: SocialLogin):
        return super().pre_social_login(request, sociallogin)

    def new_user(self, request, sociallogin: SocialLogin):
        return super().new_user(request, sociallogin)

    def populate_user(self, request, sociallogin: SocialLogin, data):
        print(sociallogin)
        print(data)
        return super().populate_user(request, sociallogin, data)

    def save_user(self, request, sociallogin: SocialLogin, form=None):
        print(sociallogin)
        print(form)
        return super().save_user(request, sociallogin, form)
