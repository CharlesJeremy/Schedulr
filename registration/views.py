from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth import login

from .forms import SchedulrUserCreationForm

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = SchedulrUserCreationForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        ret = super(RegisterView, self).post(request, *args, **kwargs)
        if self.object is not None:
            login(request, self.object)
        return ret

