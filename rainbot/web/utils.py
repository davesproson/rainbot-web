import datetime

from .models import RainDrop

def raindrop_counts(rainbot):
    now = datetime.datetime.utcnow()

    today = RainDrop.objects.filter(
        rainbot__pk=rainbot,
        time__gte=now.replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    week_start = (now - datetime.timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    this_week = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=week_start
    ).count()

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    this_month = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=month_start
    ).count()

    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0,
                             microsecond=0)

    this_year = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=year_start
    ).count()

    all_time = RainDrop.objects.filter(rainbot__pk=rainbot).count()

    return {
        'today': today,
        'this_week': this_week,
        'this_month': this_month,
        'this_year': this_year,
        'all_time': all_time
    }
