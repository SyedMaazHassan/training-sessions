from os import stat
import re
from traceback import print_tb
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import *
import json
from django.contrib.auth import login, logout
import time
from django.db.models import Q
import re
import uuid
from django.contrib.auth import user_logged_in
from django.dispatch.dispatcher import receiver
from django.shortcuts import get_object_or_404


# Signals to add device in loggged in device 
@receiver(user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    request.session.save()
    session_id = request.session.session_key
    new_device = Device(user=user, session_id = session_id)
    new_device.set_browser_info(request)
    is_exists = new_device.is_already_exists()
    if is_exists:
        new_device = is_exists
        new_device.session_id = session_id

    if new_device.is_limit_reached() and not is_exists:
        messages.error(request, "You have reached maximum Sessions limit!")
        print("Loging out")
        logout(request)
        return

    new_device.save()



    # remove other sessions
    print("-------------------")      
    # return redirect("profile")  
    # save current session
    print("-------------------")

    # create a link from the user to the current session (for later removal)
    # UserSession.objects.get_or_create(
    #     user=user,
    #     session_id=request.session.session_key
    # )



@login_required
def profile(request):
    user_form = UserForm(instance=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST)
        user = User.objects.get(id=request.user.id)
        user.first_name = request.POST.get("first_name") if request.POST.get(
            "first_name") else user.first_name
        user.last_name = request.POST.get("last_name") if request.POST.get(
            "last_name") else user.last_name
        user.username = request.POST.get(
            "email") if request.POST.get("email") else user.username
        user.save()
        user_form = UserForm(instance=user)
        messages.success(request, "Profile has been updated")

    device_sessions = Device.objects.filter(user = request.user)
    context = {'user_form': user_form, "page": "profile", 'device_sessions': device_sessions}
    return render(request, "profile.html", context)


@login_required
def search(request):
    query = request.GET.get("query")
    all_folders = all_bookmarks = all_terms = None
    bookmarks_queryset = Bookmark.objects.filter(user=request.user)
    terms_queryset = Term.objects.filter(user=request.user)
    if query:
        all_folders = Folder.objects.filter(
            user=request.user, name__icontains=query)
        all_bookmarks = bookmarks_queryset.filter(
            Q(content__icontains=query) | Q(title__icontains=query))
        all_terms = terms_queryset.filter(
            Q(content__icontains=query) | Q(title__icontains=query))
        print(all_terms)
    context = {
        'page': 'dashboard',
        'all_folders': all_folders,
        'all_bookmarks': all_bookmarks,
        'all_terms': all_terms,
        'not_found': True if not (all_folders or all_bookmarks or all_terms) else False,
        'page': 'search'
    }
    return render(request, "search.html", context)


@login_required
def delete_folder(request, folder_id):
    folder = Folder.objects.filter(user=request.user, id=folder_id).first()
    if folder:
        folder.delete()
        messages.success(request, "Folder has been deleted successfully")
    else:
        messages.error(
            request, "Folder with this id doesn't exist or you don't have access to delete it")
    return redirect("folders")


@login_required
def folders(request):
    all_folders = Folder.objects.filter(user=request.user)
    context = {'all_folders': all_folders, 'page': 'folders'}
    return render(request, "folders.html", context)


def single_term(request, folder_id, term_id):
    pass


@login_required
def create_single_term(request, folder_id):
    folder = Folder.objects.filter(id=folder_id, user=request.user).first()
    if not folder:
        messages.error(
            request, "Folder doesn't exist or you don't have access")
        return redirect("folders")

        content = ""
    operation = "Create"
    my_initial = None
    term = None
    query_title = request.GET.get("title")
    if query_title:
        my_initial = {"title": query_title}
    term_form = TermForm(request.user, initial=my_initial)

    if term_id:
        operation = "Update"
        term = Term.objects.filter(user=request.user, id=term_id).first()
        if not term:
            messages.error(request, "Term with this id doesn't exists!")
            return redirect("journal")

        term_form = TermForm(request.user, instance=term)
        content = term.content

    if request.method == "POST":
        content = request.POST.get('content')
        term_form = TermForm(request.user, request.POST, instance=term)
        if term_form.is_valid() and content:
            new_term_data = term_form.cleaned_data
            if term_id:
                term_to_save = term
                variable = "updated"
            else:
                term_to_save = Term()
                term_to_save.user = request.user
                variable = "saved"
            term_to_save.title = new_term_data['title']
            term_to_save.category = new_term_data['category']
            term_to_save.typee = new_term_data['typee']
            term_to_save.content = content
            term_to_save.save()
            term_to_save.topics.set(new_term_data['topics'])
            messages.success(
                request, f'Term has been {variable} successfully!')
            return redirect("open_term", term_id=term_to_save.id)

    context = {
        'operation': operation,
        'page': 'journal',
        'term_form': term_form,
        'content': content
    }
    return render(request, 'create_term.html', context)


@login_required
def single_folder(request, folder_id, term_id=None):
    folder = Folder.objects.filter(id=folder_id, user=request.user).first()
    if not folder:
        messages.error(
            request, "Folder doesn't exist or you don't have access")
        return redirect("folders")

    filter_type_list = ['all', 'word', 'phrase', 'term']
    filter_type = request.GET.get('type')
    term_form = TermForm(request.user)
    bookmark_form = BookmarkForm(request.user)
    modal_to_show = False
    single_term = None
    terms_query = Term.objects.filter(user=request.user, folder=folder)
    bookmark_list = []

    if term_id:
        single_term = terms_query.filter(id=term_id).first()
        bookmark_form = BookmarkForm(request.user, single_term, initial={
                                     'source': single_term})
        if not single_term:
            messages.error(request, "Term with this id doesn't exist!")
            return redirect("single-folder", folder_id=folder_id)

        if request.method == "POST":
            bookmark_form = BookmarkForm(
                request.user, single_term, request.POST)
            if bookmark_form.is_valid():
                data = bookmark_form.cleaned_data

                if is_bookmark_exist(request.user, data['title']):
                    messages.error(
                        request, "Bookmark with this title already exists!")
                else:
                    new_bookmark = Bookmark(**data)
                    new_bookmark.save()
                    bookmark_form = BookmarkForm(request.user)
                    messages.success(
                        request, "Bookmark has been added successfully!")
                    # return redirect("bookmarks")

        # Getting all the bookmarks
        bookmark_queryset = Bookmark.objects.filter(
            user=request.user, source=single_term)
        for bookmark in bookmark_queryset:
            bookmark_list.append(bookmark.get_json())
    # all_terms = terms_query.values_list("id", "title", "created_at")
    if filter_type and filter_type in filter_type_list[1:]:
        terms_query = terms_query.filter(typee=filter_type.capitalize())

    all_terms = terms_query.values_list("id", "title", "created_at")
    bookmark_list = json.dumps(bookmark_list)
    context = {
        'filter_type_list': filter_type_list,
        'page': 'folders',
        'term_form': term_form,
        'modal_to_show': modal_to_show,
        'all_terms': all_terms,
        'single_term': single_term,
        'bookmark_form': bookmark_form,
        'folder': folder,
        'bookmark_list': bookmark_list
    }
    return render(request, 'folder.html', context)


@login_required
def create_folder(request):
    if request.method == "POST":
        try:
            folder_form = FolderForm(request.POST)
            new_folder = Folder(name=request.POST.get(
                "name"), user=request.user, is_delete_allowed=True)
            new_folder.save()
            messages.success(request, "Folder has been created successfully!")
        except:
            messages.error(request, "Something went wrong")

    return redirect("folders")


@login_required
def delete_bookmark(request, bookmark_id):
    bookmark_obj = Bookmark.objects.filter(
        user=request.user, id=bookmark_id).first()
    if bookmark_obj:
        bookmark_obj.delete()
        messages.success(request, "Bookmark has been deleted successfully")
    else:
        messages.error(
            request, "Bookmark with this id doesn't exist or you don't have access to delete it")
    return redirect("bookmarks")


@login_required
def bookmarks(request):
    all_bookmarks = Bookmark.objects.filter(user=request.user)
    context = {
        'all_bookmarks': all_bookmarks,
        'page': 'bookmarks'
    }
    return render(request, "bookmarks.html", context)


def learn_bookmark(request, bookmark_id):
    output = {"status": False, "data": {}}
    bookmark = Bookmark.objects.filter(
        user=request.user, id=bookmark_id).first()
    if bookmark:
        output['data']["type"] = "bookmark"
        output['data']['object'] = {}
        output["data"]["object"]["id"] = bookmark.id
        output["data"]["object"]["title"] = bookmark.title
        output["data"]["object"]["source"] = bookmark.source.id if bookmark.source else None
        output["data"]["object"]["content"] = bookmark.content
        output["data"]["object"]["category"] = bookmark.source.category.name if (
            bookmark.source and bookmark.source.category) else None
        output["data"]["object"]["topics"] = list(
            bookmark.source.topics.all().values_list("name"))
        output["status"] = True
    return JsonResponse(output)


def learn_term(request, term_id):
    output = {"status": False, "data": {}}
    term = Term.objects.filter(user=request.user, id=term_id).first()
    if term:
        output["data"]["type"] = "term"
        output['data']['object'] = {}
        output["data"]["object"]["id"] = term.id
        output["data"]["object"]["title"] = term.actual_title()
        output["data"]["object"]["content"] = term.content
        output["data"]["object"]["category"] = term.category.name if term.category else None
        output["data"]["object"]["topics"] = list(
            term.topics.all().values_list("name"))
        output["status"] = True

        bookmark_list = []
        bookmark_queryset = Bookmark.objects.filter(
            user=request.user, source=term)
        for bookmark in bookmark_queryset:
            bookmark_list.append(bookmark.get_json())
        output["data"]["object"]["bookmarks"] = bookmark_list

    return JsonResponse(output)


def new_learn_by_query(request):
    output = {"status": False, "data": {}}

    if not request.user.is_authenticated:
        return JsonResponse(output)

    query = request.GET.get("query")
    if request.method == 'GET' and query:
        new_learning = Learning(user=request.user, query=query)
        # filtering from bookmarks
        bookmark = Bookmark.objects.filter(
            user=request.user, title__iexact=query).first()
        if bookmark:
            output["data"]["bookmark"] = {}
            new_learning.bookmark = bookmark
            output["data"]["bookmark"]["id"] = bookmark.id
            output["data"]["bookmark"]["title"] = bookmark.title
            output["data"]["bookmark"]["content"] = bookmark.content
            output["data"]["bookmark"]["category"] = bookmark.source.category.name if bookmark.source.category else None
            output["data"]["bookmark"]["topics"] = list(
                bookmark.source.topics.all().values_list("name"))

        # filter in term
        term = Term.objects.filter(
            user=request.user, title__iexact=query).first()
        if term:
            output["data"]["term"] = {}
            new_learning.term = term
            output["data"]["term"]["id"] = term.id
            output["data"]["term"]["title"] = term.actual_title()
            output["data"]["term"]["content"] = term.content
            output["data"]["term"]["category"] = term.category.name if term.category else None
            output["data"]["term"]["topics"] = list(
                term.topics.all().values_list("name"))

        new_learning.save()
        output["status"] = True
        output["not_found"] = True if not (term or bookmark) else False

    return JsonResponse(output)


def learn_by_query(request):
    output = {"status": False, "data": {}}

    if not request.user.is_authenticated:
        return JsonResponse(output)

    query = request.GET.get("query")
    not_found = request.GET.get("not_found")
    actual_query = request.GET.get("actual_query")
    typee = request.GET.get("type")

    print(request.GET)

    if request.method == "GET" and query:
        new_learning = Learning(user=request.user, query=actual_query)
        output["status"] = True
        if not_found == 'false':
            term = Term.objects.filter(id=query).first()
            if term:
                output["data"]["title"] = term.actual_title()
                output["data"]["content"] = term.content
                output["data"]["category"] = term.category.name if term.category else None
                output["data"]["topics"] = list(
                    term.topics.all().values_list("name"))
                new_learning.term = term
            else:
                output["status"] = False
        new_learning.save()

    return JsonResponse(output)


@login_required
def delete_term(request, term_id):
    term = Term.objects.filter(user=request.user, id=term_id).first()
    folder_id = term.folder.id
    if term:
        term.delete()
        messages.error(request, "Term has been deleted successfully!")
    else:
        messages.error(request, "Term with this id doesn't exists!")
    return redirect("single-folder", folder_id=folder_id)


@login_required
def create_term(request, term_id=None):
    content = ""
    operation = "Create"
    my_initial = {}
    term = None
    query_title = request.GET.get("title")
    folder_id = request.GET.get("folder_id")
    if folder_id and folder_id.isdigit():
        folder = Folder.objects.filter(user=request.user, id=folder_id).first()
        my_initial['folder'] = folder
    if query_title:
        my_initial['title'] = query_title
    term_form = TermForm(request.user, initial=my_initial)

    if term_id:
        operation = "Update"
        term = Term.objects.filter(user=request.user, id=term_id).first()
        if not term:
            messages.error(request, "Term with this id doesn't exists!")
            return redirect("journal")

        term_form = TermForm(request.user, instance=term)
        content = term.content

    if request.method == "POST":
        content = request.POST.get('content')
        term_form = TermForm(request.user, request.POST, instance=term)
        if term_form.is_valid() and content:
            new_term_data = term_form.cleaned_data
            if term_id:
                term_to_save = term
                variable = "updated"
            else:
                term_to_save = Term()
                term_to_save.user = request.user
                variable = "saved"
            term_to_save.folder = new_term_data['folder']
            term_to_save.title = new_term_data['title']
            term_to_save.category = new_term_data['category']
            term_to_save.typee = new_term_data['typee']
            content = content.replace("\n", " ")
            content = content.replace("\r", " ")
            content = content.replace("\t", " ")
            content = re.sub(' {2,}', ' ', content)
            term_to_save.content = content
            term_to_save.save()
            term_to_save.topics.set(new_term_data['topics'])
            messages.success(
                request, f'Term has been {variable} successfully!')
            return redirect("single-term", folder_id=term_to_save.folder.id, term_id=term_to_save.id)

    if term:
        folder_context = term.folder
    elif folder_id:
        folder_context = folder
    else:
        folder_context = None

    context = {
        'operation': operation,
        'page': 'folders',
        'term_form': term_form,
        'content': content,
        'folder': folder_context
    }
    return render(request, "create_term.html", context)


def is_bookmark_exist(user_object, bookmark_title):
    return Bookmark.objects.filter(
        user=user_object,
        title__iexact=bookmark_title).exists()


@login_required
def journal(request, term_id=None):
    filter_type_list = ['all', 'word', 'phrase', 'term']
    filter_type = request.GET.get('type')
    term_form = TermForm(request.user)
    bookmark_form = BookmarkForm(request.user)
    modal_to_show = False
    single_term = None

    terms_query = Term.objects.filter(user=request.user)

    if term_id:
        single_term = terms_query.filter(id=term_id).first()
        bookmark_form = BookmarkForm(request.user, single_term, initial={
                                     'source': single_term})
        if not single_term:
            messages.error(request, "Term with this id doesn't exist!")
            return redirect("journal")

        if request.method == "POST":
            bookmark_form = BookmarkForm(
                request.user, single_term, request.POST)
            if bookmark_form.is_valid():
                data = bookmark_form.cleaned_data

                if is_bookmark_exist(request.user, data['title']):
                    messages.error(
                        request, "Bookmark with this title already exists!")
                else:
                    new_bookmark = Bookmark(**data)
                    new_bookmark.save()
                    messages.success(
                        request, "Bookmark has been added successfully!")

                    # return redirect("bookmarks")

    # all_terms = terms_query.values_list("id", "title", "created_at")
    if filter_type and filter_type in filter_type_list[1:]:
        terms_query = terms_query.filter(typee=filter_type.capitalize())

    all_terms = terms_query.values_list("id", "title", "created_at")

    context = {
        'filter_type_list': filter_type_list,
        'page': 'journal',
        'term_form': term_form,
        'modal_to_show': modal_to_show,
        'all_terms': all_terms,
        'single_term': single_term,
        'bookmark_form': bookmark_form
    }
    return render(request, 'journal.html', context)

# main page function


@login_required
def index(request):
    all_folders = Folder.objects.filter(user=request.user)[0:3]
    all_bookmarks = Bookmark.objects.filter(user=request.user)[0:3]
    all_terms = Term.objects.filter(user=request.user)[0:3]
    context = {
        'page': 'dashboard',
        'all_folders': all_folders,
        'all_bookmarks': all_bookmarks,
        'all_terms': all_terms
    }
    return render(request, 'index.html', context)


@login_required
def learn(request):
    to_open = None
    bookmark_form = BookmarkForm(request.user)
    serialized_learnings = {}
    previous_learnings = Learning.objects.filter(user=request.user)

    if request.method == "POST":
        source_input = request.POST.get("source_input")
        print(request.POST)
        source = Term.objects.get(id=source_input) if source_input else None
        bookmark_form = BookmarkForm(request.user, source, request.POST)
        if bookmark_form.is_valid():
            data = bookmark_form.cleaned_data

            if is_bookmark_exist(request.user, data['title']):
                messages.error(
                    request, "Bookmark with this title already exists!")
            else:
                new_bookmark = Bookmark(**data)
                new_bookmark.save()
                bookmark_form = BookmarkForm(request.user)
                to_open = source.id
                print("==================")
                print(source.id)
                print("==================")
                messages.success(
                    request, "Bookmark has been added successfully!")
                # return redirect("bookmarks")

    context = {
        'page': 'learn',
        'bookmark_form': bookmark_form,
        'previous_learning': previous_learnings,
        'serialized_learnings': json.dumps(serialized_learnings),
        'to_open': to_open
    }

    term_query = Term.objects.filter(user=request.user).order_by("title")
    all_titles = json.dumps(list(term_query.values_list("id", "title")))
    all_bookmarks_queryset = Bookmark.objects.filter(
        user=request.user).order_by("title")
    all_bookmarks_titles = json.dumps(
        list(all_bookmarks_queryset.values_list("id", "title")))
    context["titles_array"] = all_titles
    context["titles_boomark"] = all_bookmarks_titles
    return render(request, 'learn.html', context)


@login_required
def topics(request):
    all_topics = Topic.objects.filter(user=request.user)
    context = {
        'page': 'topics',
        'all_topics': all_topics
    }
    return render(request, 'topics.html', context)


@login_required
def add_topics(request):
    if request.method == "POST":
        topic_list = request.POST.get('topics')
        if topic_list:
            topic_list = json.loads(topic_list)
            if len(topic_list) > 0:
                all_topics_of_user = Topic.objects.filter(user=request.user)
                for topic in topic_list:
                    if not all_topics_of_user.filter(name=topic).exists():
                        new_topic = Topic(name=topic, user=request.user)
                        new_topic.save()
                messages.success(
                    request, "Topics have been added successfully!")

    return redirect("create-single-term")


@login_required
def delete_topic(request, id):
    topics = Topic.objects.filter(id=id, user=request.user)
    if topics.first():
        topics.first().delete()
        messages.success(request, "Topic has been deleted successfully!")
    else:
        messages.error(
            request, "This topic doesn't exist or you don't have access to delete it!")
    return redirect("topics")


@login_required
def categories(request):
    all_categories = Category.objects.filter(user=request.user)
    context = {
        'page': 'categories',
        'all_categories': all_categories
    }
    return render(request, 'categories.html', context)


@login_required
def delete_category(request, id):
    category = Category.objects.filter(id=id, user=request.user)
    if category.first():
        category.first().delete()
        messages.success(request, "Category has been deleted successfully!")
    else:
        messages.error(
            request, "This category doesn't exist or you don't have access to delete it!")
    return redirect("categories")


@login_required
def add_catgories(request):
    if request.method == "POST":
        category_list = request.POST.get('categories')
        if category_list:
            category_list = json.loads(category_list)
            if len(category_list) > 0:
                all_categories_of_user = Category.objects.filter(
                    user=request.user)
                for category in category_list:
                    if not all_categories_of_user.filter(name=category).exists():
                        new_cat = Category(name=category, user=request.user)
                        new_cat.save()
                messages.success(
                    request, "Categories have been added successfully!")

    return redirect("create-single-term")

# function for signup


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")

    user_form = UserForm()
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            messages.success(request, "You have beem registered successfully!")

            folder_names = ["Term Papers", "Quizzes", "Project"]
            for folder in folder_names:
                new_folder = Folder(name=folder, user=new_user)
                new_folder.save()
            return redirect("signin")

    context = {'user_form': user_form}
    return render(request, "signup.html", context)


# function for login

def signin(request):
    if request.user.is_authenticated:
        return redirect("index")

    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data
            # print(user)
            print("============= LOGIN IN START ===============")
            login(request, user)
            print("============= LOGIN IN END ===============")
            return redirect("index")

            

            # if new_device.is_already_exists():
            #     login(request, login_form.cleaned_data)
            #     return redirect("index")
            # else:
            #     if new_device.is_limit_reached():
            #         messages.error(request, 'Max Account Limit Reached!!')
            #         return redirect("index")
            #     else:
            #         new_device.save()
            #         login(request, login_form.cleaned_data)
            #         return redirect("index")

    return render(request, "login.html", {'login_form': login_form})


# function for logout
def signout(request):
    logout(request)
    return redirect("signin")


# Function for checking the browser, IP-address, and device info of the user
def get_browser_info(request):

    # status of mobile, pc or tablet
    is_mobile = request.user_agent.is_mobile
    is_tablet = request.user_agent.is_tablet 
    is_pc = request.user_agent.is_pc

    # fetching the browser info
    browser_family = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version

    # fetching the os info
    os_family = request.user_agent.os.family
    os_version = request.user_agent.os.version

    # fetching the device info
    device_name = request.user_agent.device.family
    ip = get_client_ip(request)

    test = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    str = f'The {request.user.last_name} is on the Mobile: {is_mobile}\nThe {request.user.last_name} is on the Tablet: {is_tablet}\nThe {request.user.last_name} is on the PC: {is_pc}\nThe {request.user.last_name} Browser is: {browser_family}\nThe {request.user.last_name} Browser Version is: {browser_version}\nThe {request.user.last_name} OS is: {os_family}\nThe {request.user.last_name} OS Version is: {os_version}\nThe {request.user.last_name} Device is: {device_name}\n\n{test}'
    # print(test)
    # print(type(test))


    # joins elements of getnode() after each 2 digits.
    # using regex expression
    print("The MAC address in formatted and less complex way is : ", end="")
    print(':'.join(re.findall('..', '%012x' % uuid.getnode())))

    print(ip)
    return HttpResponse(str)

@login_required
def delete_user_device(request, device_id):
    # filtering if the device with the given id exists or not 
    # device = Device.objects.filter(id=device_id) 
    device = get_object_or_404(Device, pk=device_id)

    if device.user == request.user:
        device.delete()
        return HttpResponseRedirect(reverse('profile'))
    else:
        return HttpResponseRedirect(reverse('profile'))


# Function to Render the All Trainings Page 
def all_trainings(request):
    trainings = Training.objects.all()
    context = {
        'trainings' : trainings
    }
    return render(request, 'all_trainings.html', context)
    
    
# Function to Render the All Modules Page 
def all_modules(request, training_id):
    training = Training.objects.get(id=training_id)
    modules = Module.objects.filter(training=training)
    context = {
        'training' : training,
        'modules' : modules
    }
    return render(request, 'all_modules.html', context)

# Function to render a single video page
def video(request, module_id):
    module = Module.objects.get(id=module_id)
    media = Media.objects.filter(module=module)
    print(media[0])
    # if len(media) > 1:
    #     first_media = media[0]
    # else:
    #     first_media = media 
    context = {
        'module' : module,
        'medias' : media,
        'first_media' : media[0]
    }
    return render(request, 'video.html', context)