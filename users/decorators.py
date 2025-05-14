from django.http import HttpResponseForbidden


def librarian_required(view_func):
    """Decorator to restrict access to librarians only"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.userprofile.is_librarian():
            return HttpResponseForbidden("Access Denied: Librarians Only")
        return view_func(request, *args, **kwargs)
    return wrapper


def patron_required(view_func):
    """Decorator to restrict access to patrons only"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_patron():
            return HttpResponseForbidden("Access Denied: Patrons Only")
        return view_func(request, *args, **kwargs)
    return wrapper
