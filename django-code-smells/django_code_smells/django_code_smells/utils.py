from debug_toolbar.middleware import show_toolbar


# fix the issue with docker-compose network
def show_debug_toolbar(request):
    if request.headers.get("Host", "").startswith("django:8000"):
        return True
    return show_toolbar(request)
