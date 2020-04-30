import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import RainBot, RainDrop

# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'web/index.html')


@method_decorator(csrf_exempt, name='dispatch')
class PostDataView(View):
    def post(self, request):
        key = request.POST.get('api_key')
        bot_pk = request.POST.get('rainbot')

        time = float(request.POST.get('time'))
        try:
            time = datetime.datetime.utcfromtimestamp(time)
        except Exception:
            time = datetime.datetime.utcnow()

        try:
            data = float(request.POST.get('data'))
        except Exception:
            return HttpResponse(status=400)

        rainbot = get_object_or_404(RainBot, pk=bot_pk)
        if rainbot.access_key != key:
            return HttpResponse(status=403)

        RainDrop(rainbot=rainbot, time=time, data=data).save()
        return HttpResponse(status=202)
