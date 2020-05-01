import datetime
import math

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import RainBot, RainDrop
from .utils import (raindrop_counts, day_start, week_start, month_start,
                    year_start)

import pandas as pd

# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(
            request, 'web/index.html',
            {
                'counts': raindrop_counts(1)
            }
        )


class CountsView(View):
    def get(self, request):
        return JsonResponse({
            'counts': raindrop_counts(1)
        })


class GetDataView(View):
    def get(self, request):
        def do_agg(data, agg):
            if agg:
                return math.floor(data)
            return data

        since = datetime.datetime.utcfromtimestamp(
            float(request.GET.get('since') or 0)
        )
        agg = request.GET.get('aggregate')

        rainbot = get_object_or_404(RainBot, pk=request.GET.get('rainbot'))
        drops = rainbot.drops.filter(time__gte=since).order_by('time')

        time = [do_agg(d.time.timestamp(), agg) for d in drops]
        rain = [d.data for d in drops]

        series = pd.Series(rain, index=time)
        if agg:
            series = series.groupby(series.index).sum()

        return JsonResponse({
            'time': [float(i) for i in series.index],
            'rain': [float(i) for i in series.values]
        })


@method_decorator(csrf_exempt, name='dispatch')
class PostDataView(View):
    def post(self, request):
        key = request.POST.get('api_key')
        bot_pk = request.POST.get('rainbot')

        time = request.POST.get('time')
        try:
            time = datetime.datetime.utcfromtimestamp(float(time))
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

    def get(self, request):
        key = request.GET.get('api_key')
        bot_pk = request.GET.get('rainbot')

        time = request.GET.get('time')
        try:
            time = datetime.datetime.utcfromtimestamp(float(time))
        except Exception:
            time = datetime.datetime.utcnow()

        try:
            data = float(request.GET.get('data'))
        except Exception:
            return HttpResponse(status=400)

        rainbot = get_object_or_404(RainBot, pk=bot_pk)
        if rainbot.access_key != key:
            return HttpResponse(status=403)

        RainDrop(rainbot=rainbot, time=time, data=data).save()
        return HttpResponse(status=202)


class StaticDataView(View):

    @staticmethod
    def aggregator(index_attr, reindex):
        def agg(x):
            attr = getattr(x.index, index_attr)
            return x.groupby(attr).sum().reindex(reindex).fillna(0)
        return agg


    def get(self, request):
        date_map = {
            'today': day_start,
            'week': week_start,
            'month': month_start,
            'year': year_start
        }

        agg_map = {
            'today': self.aggregator('hour', range(24)),
            'week': self.aggregator('weekday', range(7)),
            'month': self.aggregator('day', range(1, 32))
        }

        label_map = {
            'today': list(range(24)),
            'week': ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
            'month': list(range(1, 32))
        }

        now = datetime.datetime.utcnow()
        rainbot = get_object_or_404(RainBot, pk=request.GET.get('rainbot'))
        context = request.GET.get('context')

        raindrops = RainDrop.objects.filter(
            rainbot=rainbot, time__gte=date_map[context](now)
        )

        try:
            data = agg_map[context](pd.Series(
                [d.data for d in raindrops],
                index=[d.time for d in raindrops]
            ))
        except:
            raise
            data = pd.Series([0] * len(label_map[context]),
                             index=label_map[context])

        return JsonResponse({
            'labels': label_map[context],
            'data': [float(i) for i in data.values]
        })
