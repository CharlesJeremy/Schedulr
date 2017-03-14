import os
from subprocess import Popen

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@require_POST
@csrf_exempt
def deploy(request):
    """ Called by GitHub webhook. """
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        script_path = os.path.join(settings.BASE_DIR, 'deploy/bin/deploy.sh')
        Popen(['sudo', script_path], stdin=None, stdout=None, stderr=None, close_fds=True)
        return HttpResponse('deploying')

    return HttpResponse(status=204)
