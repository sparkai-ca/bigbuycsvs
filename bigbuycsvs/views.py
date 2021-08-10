
from django.http import HttpResponse
from django.shortcuts import render

from utils import main



def index(request):
    '''
    index.html handler
    '''

    if request.method == 'GET':
        links_ = None
        value4PS, value4P, value4PF = '', '', ''
        with open('./utils/links.json') as fl:
            links_ = json.load(fl)
            print(links_)
        if links_:
            print('P:', links_.products_link, '\nPS:',links_.products_sotcks_link, '\nPF:', links_.products_full_link)

            # Getting the links of files
            value4PS = links_.products_sotcks_link
            value4P = links_.products_link
            value4PF = links_.products_full_link
        return render(request, "index.html", {'key4P':value4P, 'key4PS':value4PS, 'key4PF':value4PF})
        
