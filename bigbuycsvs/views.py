
from django.http import HttpResponse
from django.shortcuts import render

from threading import Timer,Thread,Event, active_count

from utils import main

# timer handler class
class TimerHandler():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()


# Initialising global variables
secs = 86000
thread = None


def index(request):
    '''
    index.html handler
    '''
    
    global thread

    if request.method == 'POST':

        # Here we are getting days and hours selection from webpage
        days = request.POST.get('days')
        hours = request.POST.get('hours')

        # converting the days and hours into seconds for scheduling
        secs = round(int(days)*24*60*60 + int(hours)*60*60)/360
        if secs == 0:
            secs = 60
        print('secs: ', secs)

        # Kill the previous thread
        if thread:
            thread.cancel()
            del thread
            thread = None
            print('canceled', thread)


        else:
            print('not canceled', thread)
        # Running the function that authenticates, uploads the csvs on the drive and generates links
        main.main()

        # Making the new thread that schedules the functions
        try:
            thread = TimerHandler(secs,main.main)
            thread.start()
        except Exception as ex:
            print(ex)

        print('waiting for', secs)

        print(thread, active_count())

        return render(request, "index.html")

    elif request.method == 'GET':
        print('P:', main.products_link, '\nPS:',main.products_sotcks_link, '\nPF:', main.products_full_link)

        # Getting the links of files
        value4PS = main.products_sotcks_link
        value4P = main.products_link
        value4PF = main.products_full_link
        return render(request, "index.html", {'key4P':value4P, 'key4PS':value4PS, 'key4PF':value4PF})
        
