from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, Http404 #, StreamingHttpResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .models import Category,Article,ItemCounter,WebCounter,Image,Signature
from .forms import Add_Comment,Compose_Form,Image_Form
import datetime
from django.views.generic.edit import FormView
from io import BytesIO
from PIL import Image
import base64
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
import json
from django.contrib.sites.shortcuts import get_current_site
chat_started = False

def index(request):
    todaytag = str(datetime.date.today())
    ct = WebCounter(datestr=todaytag) if not WebCounter.objects.filter(datestr=todaytag) else WebCounter.objects.get(datestr=todaytag)
    ct.counts += 1
    ct.save()
    latest_article_list = Article.objects.filter(display=True,contributor_author=None).order_by('-pub_date')[:20]
    context = {'latest_article_list': latest_article_list, 'categories':Category.objects.all()}
    return render(request,'blog_t/index.html',context)

@staff_member_required()
def start_comm(request):
    current_domain = get_current_site(request).domain
    startchat(current_domain)     #current_domain.split(':')[0]
    return render(request,'messages.html',{'messages':[current_domain]})  #'Server started'

def show_article(request,article_id):
    current_article = Article.objects.get(id=article_id)
    if not current_article.display:raise Http404
    todaytag = str(datetime.date.today())+'~'+str(current_article.title)
    ct = current_article.itemcounter_set.create(datestr=todaytag) if not ItemCounter.objects.filter(datestr=todaytag) else current_article.itemcounter_set.get(datestr=todaytag)
    ct.counts += 1
    ct.save()
    article = get_object_or_404(Article,pk=article_id)
    comments = current_article.comment_set.all()
    #images = current_article.image_set.all()
    images = current_article.image_set.filter(display=True)

    if request.method == 'POST':
        add_comment = Add_Comment(request.POST)

        if add_comment.is_valid():
            newcomment = article.comment_set.create(name=add_comment.cleaned_data['name'],post_time=datetime.datetime.now())
            newcomment.email_address = add_comment.cleaned_data['email_address']
            newcomment.writeup = add_comment.cleaned_data['writeup']
            newcomment.save()
            return render(request,'blog_t/article_detail.html',{'article':article,'comments':comments, 'images':images,'categories':Category.objects.all(),'add_comment_form':Add_Comment()})
    else:
        add_comment = Add_Comment()
    return render(request,'blog_t/article_detail.html',{'article':article,'comments':comments, 'images':images,'categories':Category.objects.all(),'add_comment_form':add_comment})

"""
def hello():
    yield 'Hello '
    yield 'there!'

def test_stream(request):
    return StreamingHttpResponse(hello())
"""

def category_list(request,category_label):
    category = get_object_or_404(Category,category_label=category_label)
    articles = Category.objects.get(category_label=category_label).article_set.filter(display=True)
    return render(request,'blog_t/article_list.html',{'header':category.category_label,'articles':articles,'categories':Category.objects.all()})

def my_articles_list(request,username):
    articles = Article.objects.filter(contributor_author=User.objects.get(username=username))
    return render(request,'blog_t/article_list.html',{'header':'My Article','articles':articles,'categories':Category.objects.all()})

def upload_image(request,username):
    articles = Article.objects.filter(contributor_author=User.objects.get(username=username))
    if request.method == 'POST':
        form = Image_Form(request.POST, request.FILES)
        if form.is_valid():
            article = Article.objects.get(id = form.cleaned_data['article'].id)
            if article in articles or User.objects.get(username=username) in User.objects.filter(is_staff=True):
                newimage = article.image_set.create(caption = form.cleaned_data['caption'], img_file = form.cleaned_data['img_file'])
                newimage.save()
                return render(request,'messages.html',{'messages':['Image upload success.'],'categories':Category.objects.all()})
            else:
                return render(request,'messages.html',{'messages':['Please attach the image to any of your article.'],'categories':Category.objects.all()})
    else:
        form = Image_Form()
    return render(request,'blog_t/upload_image.html',{'form':form,'articles':articles,'categories':Category.objects.all()})

@login_required()
def compose(request,username):
    if request.method == 'POST':
        form = Compose_Form(request.POST)
        if form.is_valid():
            newarticle = Article.objects.create(title = form.cleaned_data['title'])
            newarticle.writeup = form.cleaned_data['writeup']
            author_user = User.objects.get(username=username)
            newarticle.category = Category.objects.get(category_label='From Contributors') if author_user not in User.objects.filter(is_staff=True) else None
            newarticle.contributor_author = author_user if author_user not in User.objects.filter(is_staff=True) else None
            newarticle.pub_date = datetime.datetime.now()
            newarticle.display = False
            newarticle.save()
            return render(request,'messages.html',{'messages':['Thank you for your contribution.','Your article will appear after it is approved.'],'categories':Category.objects.all()})
    else:
        form = Compose_Form()
    return render(request,'blog_t/compose.html',{'form':form,'categories':Category.objects.all()})

#manual way of adding comment
"""
def detail(request,article_id):
    current_article = Article.objects.get(id=article_id)
    todaytag = str(datetime.date.today())+'~'+str(current_article.title)
    ct = current_article.itemcounter_set.create(datestr=todaytag) if not ItemCounter.objects.filter(datestr=todaytag) else current_article.itemcounter_set.get(datestr=todaytag)
    ct.counts += 1
    ct.save()
    article = get_object_or_404(Article,pk=article_id)
    comments = current_article.comment_set.all()
    return render(request,'blog_t/detail.html',{'article':article,'comments':comments,'categories':Category.objects.all()})

def add_comment(request,article_id):
    article = get_object_or_404(Article,pk=article_id)
    newcomment = article.comment_set.create(name=request.POST['newcomment_name'],post_time=datetime.datetime.now())
    newcomment.email_address = request.POST['newcomment_email_address']
    newcomment.writeup = request.POST['newcomment_writeup']
    newcomment.save()
    return HttpResponseRedirect(reverse('blog:detail',args=(article_id,)))
"""
def signature(request):
    if request.method == 'POST':
        r_image_data = request.POST['image_data']
        r_signature_owner = request.POST['signature_owner']
        image_format, image_data = r_image_data.split(';base64,') 
        image_data = base64.b64decode(image_data)

        newsignature = Signature.objects.create(signature_owner = r_signature_owner)
        file_data = ContentFile(image_data, name = 'sg_' + r_signature_owner + '.' + image_format.split('/')[-1])
        newsignature.signature_image = file_data
        """
        #--optionat, to show image on the spot--
        image_dataIO = BytesIO(image_data)
        im = Image.open(image_dataIO)
        im.show()
        """
        try:
            newsignature.save()
            return render(request,'messages.html',{'messages':['Signature upload successful.'],'categories':Category.objects.all()})
        except:
            pass
        return render(request,'blog_t/signature.html')            
    else:
        return render(request,'blog_t/signature.html')

def board(request):
    room_name = 'board'
    return render(request, 'blog_t/board.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

def chat_lobby(request):
    return render(request, 'blog_t/chat_lobby.html', {})

def chat_room(request, room_name):
    return render(request, 'blog_t/chat_room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

def startchat(domain):
    if not chat_started:
        import socket,sys,threading,select
        joincode = 'o'
        commands = ['Send OTP','Passing entered OTP']

        class Clientthread(threading.Thread):
            def __init__(self,addr,conn):
                threading.Thread.__init__(self)
                self.addr = addr
                self.conn = conn
            def run(self):
                interact(self.addr,self.conn)
         
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        IP_address = domain #'127.0.0.1'
        Port = 8081
        server.bind((IP_address, Port))
        print('Server is up. Awaiting desktop to join')
        server.listen(100) 

        def interact(addr,conn):
            lanjut = True
            while lanjut:
                sockets_list = [sys.stdin, conn]
                read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
                for socks in read_sockets:
                    if socks == conn:
                        try:
                            message = conn.recv(2048).decode('utf-8')
                            if message:
                                 print("<" + addr[0] + "> " + message)
                        except:
                            continue
                    else:
                        command = sys.stdin.readline()
                        if command[0] in map(str,range(1,len(commands)+1)):
                            conn.send(commands[int(command[0])-1].encode('utf-8'))
                            if command[0]=='2':
                                resp = input('OTP entered by customer: ')
                                conn.send(resp.encode('utf-8'))
                        elif command[0]==str(len(commands)+1):
                            conn.close()
                            server.close()
                            print('Chat terminated')
                            chat_started = False
                            lanjut = False
         
        conn, addr = server.accept()
        jcode = conn.recv(2048).decode('utf-8')
        if jcode=='oG':
            print(addr[0] + " connected")
            con_msg = 'You are connected as a client to: '+domain+' server.'
            conn.send(con_msg.encode('utf-8'))
            thread = Clientthread(addr,conn)
            thread.start()
            print('COMMAND')
            pcommands=commands+['Quit']
            for idx in range(len(pcommands)):
                print('{:d}. {:s}'.format(idx+1,pcommands[idx]))
        else:
            conn.send(b"Failed to connect")