from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from elevenbits.blog.models import Entry
from elevenbits.menu.models import Menu
from elevenbits.page.models import Page

def index(request):
    page = Page.objects.get(title="ElevenBits")
    menu_list = Menu.objects.all()
    latest_entry_list = Entry.objects.all()[:5].reverse()
    # the context_instance will make sure that the default
    # TEMPLATE_CONTEXT_PROCESSORS are executed, among which
    # the django.core.context_processors.media.  That way
    # the MEDIA_URL will become part of the session
    return render_to_response('index.html', 
                              {'page': page,
                               'menu_list': menu_list, 
                               'latest_entry_list': latest_entry_list},
                              context_instance=RequestContext(request))

def detail(request, id):
    page = Page.objects.get(title="ElevenBits")
    menu_list = Menu.objects.all()
    entry = get_object_or_404(Entry, pk=id)
    return render_to_response('detail.html', 
                              {'page': page,
                               'menu_list': menu_list, 
                               'entry': entry},
                              context_instance=RequestContext(request))
    


#def tags(request):
    
