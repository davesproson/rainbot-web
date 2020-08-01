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


def impulse2height(impulse):
    """
    Convert an 'impulse' from rainbot to the amount of rain in mm.

    From AW:
    If the number you get is [rain] then:
    Drop Diameter = 0.705*[rain]^0.276 (from a single point cal based on 3.2mm
    droplets hitting the centre of the sensor with a presumed momentum based
    on their terminal velocity, a bit of an assumption, but still...)

    Drop volume, assuming spherical, is =4*(Drop Diameter/2)^3*pi/3 (from
    geometry lessons)

    Rainfall is usually given as a linear height in mm, so this drop
    conceptually spreads out on the sensor into a layer of
    Height = Drop Volume/(pi()*15^2)

    This last bit is a bit of a fudge factor. I made an assessment of the
    effective sensor radius by dropping the same size drops at different
    distances away from the centre of the sensor. You might think that 12mm
    looks like a better number to use. But if you do that then the measured
    rain height (and cumulative amount) will get bigger, and it’s already too
    big by about 10% vs the rain jar...

    Args:
        impulse - the raindrop signal recorded by rainbot

    Returns:
        height - impulse converted to the equivilent height (depth?) of water,
                 in mm.
    """
    diameter = 0.705 * impulse ** 0.276
    volume = (4. / 3.) * math.pi * (diameter / 2) ** 3
    height = volume / (math.pi * 15 ** 2)
    return height


# Create your views here.
class HomeView(View):
    def get(self, request):
        botname = request.GET.get('name', 'zippy')
        try:
            rainbot = RainBot.objects.get(name__iexact=botname)
        except Exception:
            return HttpResponse('Who\'s {bot}?'.format(bot=botname))

        return render(
            request, 'web/index.html',
            {
                'counts': raindrop_counts(rainbot.pk),
                'name': rainbot.name,
                'battery': rainbot.battery,
                'wifi': rainbot.wifi,
                'pk': rainbot.pk
            }
        )


class CountsView(View):
    def get(self, request):
        bot = get_object_or_404(RainBot, pk=request.GET.get('rainbot'))
        return JsonResponse({
            'counts': raindrop_counts(bot.pk)
        })


class GetDataView(View):
    def get(self, request):
        def do_agg(data, agg):
            if agg:
                return math.floor(data)
            return data

        since = datetime.datetime.utcfromtimestamp(
            math.floor(float(request.GET.get('since') or 0))
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

    def _rain(self, r, t, d):
        height = impulse2height(d)
        RainDrop(rainbot=r, time=t, data=height).save()

    def _wifi(self, r, t, d):
        r.wifi = d
        r.save()

    def _battery(self, r, t, d):
        r.battery = d
        r.save()

    EVENT_MAP = {
        'wifi': _wifi,
        'battery': _battery,
        'rain': _rain
    }

    def _oper(self, request, datain):
        key = datain.get('api_key')
        bot_pk = datain.get('rainbot')

        time = datain.get('time')
        event = datain.get('event')

        try:
            time = datetime.datetime.utcfromtimestamp(float(time))
        except Exception:
            time = datetime.datetime.utcnow()

        try:
            data = float(datain.get('data'))
        except Exception:
            return HttpResponse(status=400)

        rainbot = get_object_or_404(RainBot, pk=bot_pk)
        if rainbot.access_key != key:
            return HttpResponse(status=403)

        try:
            self.EVENT_MAP[event](self, rainbot, time, data)
        except Exception:
            raise
            return HttpResponse(status=400)

        return HttpResponse(status=202)

    def get(self, request):
        return self._oper(request, request.GET)

    def post(self, request):
        return self._oper(request, request.POST)


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
        except Exception:
            data = pd.Series([0] * len(label_map[context]),
                             index=label_map[context])

        return JsonResponse({
            'labels': label_map[context],
            'data': [float(i) for i in data.values]
        })
