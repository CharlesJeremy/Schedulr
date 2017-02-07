from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField


class SchedulrUserCreationForm(UserCreationForm):
    # http://jessenoller.com/blog/2011/12/19/quick-example-of-extending-usercreationform-in-django
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(SchedulrUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

