from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),

    path('search', views.search, name="search"),

    path('profile', views.profile, name="profile"),
    
    path('bookmarks/<bookmark_id>/delete', views.delete_bookmark, name="delete_bookmark"),
    path('bookmarks/', views.bookmarks, name="bookmarks"),

    path('learn_by_query/', views.learn_by_query, name="learn_by_query"),
    path('new_learn_by_query/', views.new_learn_by_query, name="new_learn_by_query"),
    path('bookmark/<bookmark_id>', views.learn_bookmark, name="learn_bookmark"),
    path('term/<term_id>', views.learn_term, name="learn_term"),
    path('learn/', views.learn, name="learn"),
    
    path('folders/', views.folders, name="folders"),
    path('folders/<folder_id>', views.single_folder, name="single-folder"),
    path('folders/<folder_id>/term/<term_id>', views.single_folder, name="single-term"),
    path('term/<term_id>/edit', views.create_term, name="edit_term"),
    path('folders/<folder_id>/delete', views.delete_folder, name="delete_folder"),
    path('folders/term/add', views.create_folder, name="create-folder"),

    path('terms/create', views.create_term, name="create-single-term"),

    path('journal/', views.journal, name="journal"),
    # path('journal/terms/<term_id>/edit/', views.create_term, name="edit_term"),
    path('journal/terms/<term_id>/', views.journal, name="open_term"),
    path('journal/terms/<term_id>/delete/', views.delete_term, name="delete_term"),
    path('journal/terms/create', views.create_term, name="create_term"),
    
    path('topics/', views.topics, name="topics"),
    path('add-topics/', views.add_topics, name="add-topics"),
    path('topics/<id>/delete', views.delete_topic, name="delete_topic"),
    
    path('categories/', views.categories, name="categories"),
    path('categories/<id>/delete', views.delete_category, name="delete_category"),
    path('add-catgories', views.add_catgories, name="add-catgories"),
    
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('logout/', views.signout, name="logout"),
    
    # Test path for checking the browser, IP-address, and device info of the user 
    path('browser/', views.get_browser_info, name = 'browser'),

    path('device/<int:device_id>/delete', views.delete_user_device, name = 'delete_device'),

    # Path to all trainings Page 
    path('all_trainings/', views.all_trainings, name = 'all_trainings'),

    # Path to all modules Page 
    path('all_modules/<int:training_id>/', views.all_modules, name = 'all_modules'),

    # Path to single video Page 
    path('video/<int:module_id>/', views.video, name = 'video'),

]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
