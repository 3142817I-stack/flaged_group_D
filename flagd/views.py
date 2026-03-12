from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

def index(request):
    context_dict = {}

    #visitor_cookie_handler(request)

    return render(request, 'flagd/templates/flagd/index.html', context=context_dict)

def about(request):
    return HttpResponse("Abouuuuut")

#def about(request):
#    return render(request, 'flagd/about.html')
