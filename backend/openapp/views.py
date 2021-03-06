from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core import serializers

import json, calendar

import datetime

from django.contrib.auth.models import User
from .models import Code, UserAttrib, Message, Schedule

from .utils import CodeGenerator

"""
Default index handler.
"""
def index(request):

    if request.user.is_authenticated:

        request.user.imgpath = UserAttrib.objects.get(user=request.user).imgpath

        context = {}
        context['username'] = request.user.username

        if request.user.is_staff:
            context = {}

            combined_queryset = Message.objects.filter(receiver=request.user)
            messages = combined_queryset.values('sender').distinct()

            chat_list = []

            for message in messages:
                user = User.objects.get(id=message['sender'])
                try:
                    attrib = UserAttrib.objects.get(user=user)
                    user.imgpath = attrib.imgpath
                except:
                    user.imgpath = 'img/001.png'
                print(user)
                chat_list.append(user)


            context['chat_list'] = chat_list

            return render(request, 'gcc.html', context)
        else:
            userattrib = UserAttrib.objects.get(user=request.user)

            return render(request, 'index.html', context)
    else:
        return redirect('/openapp/login')


"""
API for generating a code.
Generates a code.
Then adds code to database.
"""
def generateCode(request):

    # Generate code.
    # If code already exists,
    # generate until valid for
    # 3 tries.

    response = {}
    valid = False
    code = None
    tries = 0

    while(not valid and tries <= 3):
        code = createCode()

        if(not codeExists(code)):
            valid = True
            break

        tries = tries + 1

    # If code is valid, add to database.
    # Otherwise, tell user to try again
    # with code NULL.

    if valid and addCode(code):
        response['rc'] = 'success'
        response['code'] = code
    else:
        response['rc'] = 'failed'
        response['code'] = None

    return JsonResponse(response)


"""

"""
def register(request):

    if request.method == 'GET':
        context = {}
        return render(request, 'register.html', context)

    elif request.method == 'POST':
        refcode = request.POST.get('refcode', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        response = {}

        if not codeUsed(refcode):
            # Create user if code is valid
            try:
                user = User.objects.create_user(username=username)
                user.set_password(password)
                user.is_staff = False
                user.active = True
                user.save()
                print('Creating UserAttrib')
                attrib = UserAttrib(user=user, imgpath='img/001.png')
                attrib.save()
                print('Successful UserAttrib')
                # Invalidate code
                setCodeStatus(refcode)

                response['rc'] = 'OK'
            except:
                response['rc'] = 'NOT OK'
                response['errormessage'] = 'Invalid username or password.'
        else:
            response['rc'] = 'NOT OK'
            response['errormessage'] = 'Ref code does not exist or is already used.'

        return JsonResponse(response)


"""

"""
def loginUser(request):

    context = {}

    if request.method == 'GET':
        return render(request, 'dash.html', context)
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        print(username)
        print(password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print('user is not none')
            login(request, user)
            context['rc'] = 'OK'
        else:
            print('user is none')
            context['rc'] = 'NOT OK'
            context['errormessage'] = 'Invalid credentials.'

        return JsonResponse(context)

"""

"""
def logoutUser(request):

    logout(request)
    return redirect('/openapp/login')


def collegeprofile(request, college):

    context = {}
    context['college'] = college

    request.user.imgpath = UserAttrib.objects.get(user=request.user).imgpath

    if request.user.is_authenticated:
        # Get councilor for college
        try:
            user = User.objects.get(username__icontains=college)
            userAttrib = UserAttrib.objects.get(user=user)

            if user is not None:
                context['user'] = user
                context['firstname'] = user.first_name
                context['lastname'] = user.last_name
                context['imgpath'] = userAttrib.imgpath
            else:
                print('no user')
                context['errormessage'] = 'BAD OUTPUT'
        except:
            print('errro errors')
            context['errormessage'] = 'BAD OUTPUT'

        # Return requested info
        return render(request, 'profile.html', context)
    else:
        return redirect('/openapp/login')


def chat(request):

    context = {}

    if request.method == 'GET':
        return HttpResponse('GET')

    elif request.method == 'POST':
        sender = request.user
        receiver = User.objects.get(username=request.POST.get('college', ''))
        message = request.POST.get('message', '')

        message = Message(sender=sender, receiver=receiver, message=message)
        message.save()

        return JsonResponse(context)


def getMessages(request):
    context = {}

    receiver = request.GET['receiver']
    user = User.objects.get(username=receiver)
    combined_queryset = Message.objects.filter(sender=request.user, receiver=user) | Message.objects.filter(sender=user, receiver=request.user)
    print(combined_queryset)
    messages = combined_queryset.order_by('date_created')

    res = list(messages.values('message', 'sender', 'receiver', 'date_created'))

    context['messages'] = []

    for message in res:
        u = User.objects.get(id=message['sender'])
        message['sender'] = u.username

        u = User.objects.get(id=message['receiver'])
        message['receiver'] = u.username

        context['messages'].append(message)

    return JsonResponse(context)

def collegechat(request, college):
    context = {}

    request.user.imgpath = UserAttrib.objects.get(user=request.user).imgpath

    user = User.objects.get(username__icontains=college)
    userAttrib = UserAttrib.objects.get(user=user)
    context['imgpath'] = userAttrib.imgpath
    context['college'] = college

    combined_queryset = Message.objects.filter(sender=user, receiver=request.user) | Message.objects.filter(sender=request.user, receiver=user)
    print(combined_queryset)
    messages =  combined_queryset.order_by('date_created')
    print(messages)
    context['messages'] = messages

    return render(request, 'chat.html', context)


def appoint(request, college):
    context = {}

    request.user.imgpath = UserAttrib.objects.get(user=request.user).imgpath

    date_today = datetime.date.today()
    year_today = date_today.year
    month_today = date_today.month

    num_days = calendar.monthrange(year_today, month_today)[1]
    days = [datetime.date(year_today, month_today, day) for day in range(1, num_days+1)]

    context['today'] = date_today
    context['days'] = days
    context['college'] = college

    w = str(days[0].weekday())
    v = str(days[-1].weekday())

    if w in '0':
        context['ran'] = range(1)
    elif w in '1':
        context['ran'] = range(2)
    elif  w in '2':
        context['ran'] = range(3)
    elif w in '3':
        context['ran'] = range(4)
    elif w in '4':
        context['ran'] = range(5)
    elif w in '5':
        context['ran'] = range(6)
    elif w in '6':
        context['ran'] = range(0)

    if v in '0':
        context['end'] = range(5)
    elif v in '1':
        context['end'] = range(4)
    elif  v in '2':
        context['end'] = range(3)
    elif v in '3':
        context['end'] = range(2)
    elif v in '4':
        context['end'] = range(1)
    elif v in '5':
        context['end'] = range(0)
    elif v in '6':
        context['end'] = range(6)

    return render(request, 'appoint.html', context)


def appointments(request):
    context = {}

    request.user.imgpath = UserAttrib.objects.get(user=request.user).imgpath

    date_today = datetime.date.today()
    year_today = date_today.year
    month_today = date_today.month

    num_days = calendar.monthrange(year_today, month_today)[1]
    days = [datetime.date(year_today, month_today, day) for day in range(1, num_days + 1)]

    context['today'] = date_today
    context['days'] = days

    w = str(days[0].weekday())
    v = str(days[-1].weekday())

    if w in '0':
        context['ran'] = range(1)
    elif w in '1':
        context['ran'] = range(2)
    elif w in '2':
        context['ran'] = range(3)
    elif w in '3':
        context['ran'] = range(4)
    elif w in '4':
        context['ran'] = range(5)
    elif w in '5':
        context['ran'] = range(6)
    elif w in '6':
        context['ran'] = range(0)

    if v in '0':
        context['end'] = range(5)
    elif v in '1':
        context['end'] = range(4)
    elif v in '2':
        context['end'] = range(3)
    elif v in '3':
        context['end'] = range(2)
    elif v in '4':
        context['end'] = range(1)
    elif v in '5':
        context['end'] = range(0)
    elif v in '6':
        context['end'] = range(6)

    return render(request, 'appointments.html', context)


def createappointments(request):

    context = {}

    schedule = request.GET['schedule']
    day = request.GET['day']

    sched = Schedule(counselor=request.user, time=schedule, date=datetime.datetime.strptime(day, '%B %d, %Y').date())
    sched.save()

    context['rc'] = 'OK'
    return JsonResponse(context)

def deleteappointments(request):

    id = request.GET['id']

    sched = Schedule.objects.get(id=id)
    sched.delete()

    return JsonResponse({})

def getAppointmentSchedules(request, college):

    date_str = request.GET['day']
    sched = datetime.datetime.strptime(date_str, '%B %d, %Y').date()


    context = {}
    context['rc'] = 'OK'

    try:
        counselor = User.objects.get(username__icontains=college)
        schedules = list(Schedule.objects.filter(counselor=counselor).filter(date=sched).order_by('time').values())

        if len(schedules) > 0:
            context['schedules'] = schedules
        else:
            context['rc'] = 'NOT OK'
            context['message'] = 'No schedule available.'

    except:
        context['rc'] = 'NOT OK'


    return JsonResponse(context)


def setAppointmentSchedule(request):
    context = {}

    id = request.GET['id']
    assignee = request.GET['assignee']

    schedule = Schedule.objects.get(id=id)
    schedule.assignee = assignee
    schedule.save()

    return JsonResponse(context)

def cancelAppointment(request):
    context = {}

    id = request.GET['id']

    schedule = Schedule.objects.get(id=id)
    schedule.assignee = ''
    schedule.save()

    return JsonResponse(context)

"""
API for checking if code exists.
"""
def hasCode(request):

    code = request.GET['code']

    response = {}
    response['code'] = code

    if codeExists(code):
        response['exists'] = True
    else:
        response['exists'] = False

    return JsonResponse(response)

"""
API for getting code status.
"""
def getCodeStatus(request):

    code = request.GET['code']
    response = {}

    if codeExists(code):
        response['rc'] = 'success'
        response['code'] = code
        response['isUsed'] = codeUsed(code)
    else:
        response['rc'] = 'failed'
        response['message'] = 'No code  exists.'

    return JsonResponse(response)


"""
API for setting code is used.
"""
def setCodeAsUsed(request):

    code = request.GET['code']

    response = {}
    response['code'] = code

    if codeExists(code) and not codeUsed(code):
        setCodeStatus(code)
        response['rc'] = 'success'
        response['isUsed'] = True

    else:
        response['rc'] = 'failed'
        response['isUsed'] = False

    return JsonResponse(response)

"""
Generates a code.
"""
def createCode():

    codeGenerator = CodeGenerator()
    id = codeGenerator.getCode()

    return id

"""
Check if code already exists.
"""
def codeExists(code):

    # Check database if code exists

    isExists = False
    try:
        res = Code.objects.get(code=code)
        isExists = True
    except:
        isExists = False

    return isExists

"""
Gets code status.
"""
def codeUsed(code):

    # Check code status in database
    isError = False
    try:
        res = Code.objects.get(code=code)
        if res.used:
            isError = True
    except:
        isError = True

    return isError

"""
Sets the code is already used.
"""
def setCodeStatus(code):

    res = Code.objects.get(code=code)
    res.used = True
    res.save()

"""
Adds the code to the database
"""
def addCode(code):

    rc = True

    # Add code to the database
    newCode = Code(code=code)
    newCode.save()

    return rc


