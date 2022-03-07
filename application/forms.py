# from django import forms
# from django.

# class UserForm(forms.Form):
#     first_name = forms.CharField(max_length = 50)
#     last_name = forms.CharField(max_length = 50)
#     email  = forms.EmailField()
#     password = forms.CharField(max_length=20, widget=forms.PasswordInput)
#     confirm_password = forms.CharField(max_length=20, widget=forms.PasswordInput)

from django.contrib.auth.password_validation import validate_password
from django.core import validators
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *
import re
 
# Make a regular expression
# for validating an Email


class LoginForm(forms.Form):
    email = forms.EmailField(label = 'Email address', required = True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, help_text=None)

    def is_user_exists(self, email):
        user = User.objects.filter(email = email)
        return user.first()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = self.is_user_exists(email)
        if user:
            if not user.check_password(password):
                self.add_error('password', 'Invalid password')
                return None
            return user
        else:
            self.add_error('email', 'This email is not registered')


class BookmarkForm(forms.ModelForm):
    source_input = forms.CharField(widget=forms.HiddenInput(), required = False)

    def __init__(self, user, source=None, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args,**kwargs) # populates the post
        self.user_obj = user
        self.source_obj = source

    def get_source_object(self, source_input_id):
        query = Term.objects.filter(user = self.user_obj, id = source_input_id)
        return query.first()

    def clean(self):
        cleaned_data = super().clean()
        data_source_input = cleaned_data.get('source_input')
        new_data = cleaned_data.copy()

        if data_source_input:
            source_obj = self.get_source_object(data_source_input)
            print("====")
            print(data_source_input)
            print(source_obj)
            print("====")
            if source_obj:
                new_data['source'] = source_obj
            else:
                self.add_error('content', "Bookmark can't be added!")    
        else:
            new_data['source'] = self.source_obj

        new_data['user'] = self.user_obj
        del new_data['source_input']
        return new_data

    class Meta:
        model = Bookmark
        fields = ('title', 'content', 'comment', 'color')


class TermForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super (TermForm, self).__init__(*args,**kwargs) # populates the post
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['topics'].queryset = Topic.objects.filter(user=user)
        self.fields['folder'].queryset = Folder.objects.filter(user=user)
        self.fields['typee'].label = "Type"
        self.user_obj = user
        
    def is_term_exists(self, term_title):
        return Term.objects.filter(title__iexact=term_title, user = self.user_obj).exists()

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        if (not self.instance.id) and self.is_term_exists(title):
            self.add_error('title', 'Term with this title already exists')    

    class Meta:
        model = Term
        fields = ('title', 'category', 'topics', 'typee', 'content', 'folder')

class UserForm(UserCreationForm):
    password1=forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(
            attrs={
                "data-bs-toggle": "popover",
                "title":"Password instructions",
                "data-bs-html":"true",
                "data-bs-content":" \
                    <ul> \
                        <li class='my-2'>Your password can’t be too similar to your other personal information.<br></li> \
                        <li class='my-2'>Your password must contain at least 8 characters.<br></li> \
                        <li class='my-2'>Your password can’t be a commonly used password.<br></li> \
                        <li class='my-2'>Your password can’t be entirely numeric. </li> \
                    </ul>"
            }
        ),
        validators=[validate_password],  
        help_text=None
    )
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text=None)     
    # city = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off'}))


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def is_user_exists(self, email):
        user = User.objects.filter(email = email)
        return user.exists()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        required_fields = ["first_name", "last_name", "email"]

        # Validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        


        for i in required_fields:
            my_field = cleaned_data.get(i)

            if not my_field:
                # raise forms.ValidationError("This field is required")
                self.add_error(i, "This field is required")

        if email:
            # pass the regular expression
            # and the string into the fullmatch() method
            if not re.fullmatch(regex, email):
                self.add_error('email', 'Enter a valid email address')

            if self.is_user_exists(email):
                self.add_error('email', 'This email is already registered')


        # All test passed
        if len(self.errors) == 0:
            new_data = self.cleaned_data.copy()
            new_data['username'] = new_data['email']
            new_data['password'] = new_data['password1']
            del new_data['password1']
            del new_data['password2']
            return new_data



class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = "__all__"
        exclude = ("created_at", "is_delete_allowed", "user")