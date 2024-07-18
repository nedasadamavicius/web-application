from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request, 'WebApplication/home.html')


def profile_view(request):
    return render(request, 'WebApplication/profile.html')


def artist_view(request):
    return render(request, 'WebApplication/artist.html')
