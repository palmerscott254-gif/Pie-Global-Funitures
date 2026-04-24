from django.http import JsonResponse

from pie_global.performance import get_startup_state


def warmup_view(request):
    """Fast warmup endpoint with no DB or external service calls."""
    startup = get_startup_state()
    return JsonResponse(
        {
            'status': 'ok',
            'service': 'pie-global-backend',
            'cold_start_pending': startup['is_cold_start'],
            'uptime_ms': startup['uptime_ms'],
        },
        status=200,
    )
