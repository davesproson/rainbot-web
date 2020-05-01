import datetime

from .models import RainDrop

def day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def week_start(dt):
    return (dt - datetime.timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

def month_start(dt):
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def year_start(dt):
    return dt.replace(month=1, day=1, hour=0, minute=0, second=0,
                      microsecond=0)

def raindrop_counts(rainbot):
    now = datetime.datetime.utcnow()

    today = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=day_start(now)
    ).count()

    this_week = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=week_start(now)
    ).count()

    this_month = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=month_start(now)
    ).count()

    this_year = RainDrop.objects.filter(
        rainbot__pk=rainbot, time__gte=year_start(now)
    ).count()

    all_time = RainDrop.objects.filter(rainbot__pk=rainbot).count()

    return {
        'today': today,
        'this_week': this_week,
        'this_month': this_month,
        'this_year': this_year,
        'all_time': all_time
    }
