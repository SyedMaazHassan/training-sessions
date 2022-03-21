from django.shortcuts import render

# Create your views here.
# Function to handle the Index Page 
def index(request):
    return render(request, 'admin-panel.html', {})