from django.shortcuts import render


def index(request):
    return render(request, "browse.html", {
        'name': 'joe',
    })

