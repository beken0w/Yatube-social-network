from django.shortcuts import render


def page_not_found(request, exception):
    """Страница не найдена."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Токен не совпадает или не был передан."""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Сервер недоступен."""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)
