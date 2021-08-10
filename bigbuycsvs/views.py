
from django.http import HttpResponse
from django.shortcuts import render

from utils import main



def index(request):
    '''
    index.html handler
    '''

    if request.method == 'GET':

        with open('./utils/links.json') as fl:
            links_ = json.load(fl)
            print(links_)

        print('P:', main.products_link, '\nPS:',main.products_sotcks_link, '\nPF:', main.products_full_link)

        # Getting the links of files
        value4PS = main.products_sotcks_link
        value4P = main.products_link
        value4PF = main.products_full_link
        return render(request, "index.html", {'key4P':value4P, 'key4PS':value4PS, 'key4PF':value4PF})
        
