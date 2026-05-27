from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def test_images(request):
    return render(request, 'test_images.html')
