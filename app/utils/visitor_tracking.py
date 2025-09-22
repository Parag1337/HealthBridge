"""
Visitor tracking utilities for HealthBridge application
"""

from flask import request
from flask_login import current_user
from datetime import datetime


def log_visitor_info(page_name=None, additional_info=None):
    """
    Log comprehensive visitor information to console/server logs
    
    Args:
        page_name (str): Name of the page being visited (optional)
        additional_info (dict): Any additional information to log (optional)
    
    Returns:
        dict: Visitor information dictionary
    """
    visitor_info = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent'),
        "referrer": request.referrer,
        "method": request.method,
        "url": request.url,
        "query_string": request.query_string.decode('utf-8'),
        "accept_languages": request.headers.get('Accept-Language'),
        "host": request.host,
        "protocol": request.environ.get('SERVER_PROTOCOL'),
        "authenticated": current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
        "user_role": getattr(current_user, 'role', None) if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None,
        "user_id": getattr(current_user, 'id', None) if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
    }
    
    # Add page name if provided
    if page_name:
        visitor_info["page"] = page_name
    
    # Add any additional information
    if additional_info and isinstance(additional_info, dict):
        visitor_info.update(additional_info)
    
    # Log to console with clear formatting
    separator = "=" * 30
    print(f"\n{separator}")
    print(f"VISITOR TRACKING - {page_name.upper() if page_name else 'PAGE VISIT'}")
    print(f"{separator}")
    
    for key, value in visitor_info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"{separator}\n")
    
    return visitor_info


def get_client_ip():
    """
    Get the real client IP address, handling proxies and load balancers
    
    Returns:
        str: Client IP address
    """
    # Check for forwarded headers (common in production deployments)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, get the first one
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def get_user_location_info():
    """
    Extract location-related information from request headers
    
    Returns:
        dict: Location information
    """
    return {
        "accept_language": request.headers.get('Accept-Language'),
        "accept_encoding": request.headers.get('Accept-Encoding'),
        "accept": request.headers.get('Accept'),
        "timezone": request.headers.get('X-Timezone'),  # If frontend sends timezone
        "country": request.headers.get('CF-IPCountry'),  # Cloudflare country header
    }


def log_security_event(event_type, details=None):
    """
    Log security-related events with visitor information
    
    Args:
        event_type (str): Type of security event (login_attempt, failed_login, etc.)
        details (dict): Additional security event details
    """
    security_info = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "ip_address": get_client_ip(),
        "user_agent": request.headers.get('User-Agent'),
        "url": request.url,
        "method": request.method,
    }
    
    if details:
        security_info.update(details)
    
    print(f"\n{'='*40}")
    print(f"SECURITY EVENT: {event_type.upper()}")
    print(f"{'='*40}")
    
    for key, value in security_info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"{'='*40}\n")
    
    return security_info