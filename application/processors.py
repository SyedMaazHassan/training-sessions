from .models import Bookmark, Folder
from .forms import FolderForm


def get_all_bookmarks(request):
    if not request.user.is_authenticated:
        return {'total_bookmarks': None}

    all_bookmarks = None
    limit = 100
    
    all_bookmarks = Bookmark.objects.filter(user = request.user).values_list("id").count()
    if all_bookmarks > limit:
        all_bookmarks = f"{limit}+"

    return {
        'folder_form': FolderForm(),
        'total_bookmarks': all_bookmarks,
        'folders': Folder.objects.filter(user = request.user)
    }