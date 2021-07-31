from django.shortcuts import render


def index(request):
    f = open('./logs/django.log', 'r')
    content = []
    for i in f:
        content.insert(0, i)
    context = {'data': content}
    return render(request, 'index.html', context)


def my_day(request):
    f = open('./logs/my_day.log', 'r')
    content = []
    for i in f:
        content.insert(0, i)
    context = {'data': content}
    return render(request, 'index.html', context)


def message(request):
    f = open('./logs/message.log', 'r')
    content = []
    for i in f:
        content.insert(0, i)
    context = {'data': content}
    return render(request, 'index.html', context)
