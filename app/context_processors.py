def user_roles(request):
    user = request.user
    is_authenticated = user.is_authenticated

    return {
        'is_authenticated': is_authenticated,
        'is_librarian': is_authenticated and hasattr(user, 'userprofile') and user.userprofile.is_librarian(),
        'is_patron': is_authenticated and hasattr(user, 'userprofile') and user.userprofile.is_patron(),
    }
