from datetime import datetime, date, timezone
from flask import current_app
import pytz

def get_app_timezone():
    """Get the configured timezone for the application"""
    tz_name = current_app.config.get('TIMEZONE', 'Asia/Kolkata')
    return pytz.timezone(tz_name)

def get_current_date():
    """Get current date in the application's configured timezone"""
    app_tz = get_app_timezone()
    now = datetime.now(timezone.utc)
    local_now = now.astimezone(app_tz)
    return local_now.date()

def get_current_datetime():
    """Get current datetime in the application's configured timezone"""
    app_tz = get_app_timezone()
    now = datetime.now(timezone.utc)
    return now.astimezone(app_tz)

def get_current_time():
    """Get current time in the application's configured timezone"""
    return get_current_datetime().time()

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt is None:
        return None
    app_tz = get_app_timezone()
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(app_tz)

def local_to_utc(local_dt):
    """Convert local datetime to UTC"""
    if local_dt is None:
        return None
    app_tz = get_app_timezone()
    if local_dt.tzinfo is None:
        local_dt = app_tz.localize(local_dt)
    return local_dt.astimezone(timezone.utc)