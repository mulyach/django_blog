from django.shortcuts import render,get_object_or_404
from django.http import Http404, HttpResponse #, HttpResponseRedirect, StreamingHttpResponse
from django.template.loader import get_template
#from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .models import Category,Article,ItemCounter,WebCounter,Signature
from .forms import Add_Comment,Compose_Form,Image_Form
import datetime,base64,json,os
from .commCls import wscomm
#from io import BytesIO
#from PIL import Image
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site
#chat_started = False   #TO BE DELETED
max_attempt = 2
cs_chat_ready_def = True
temp_ROOM_OTP = '__otpr__'
temp_ROOM_CS_MASTER = '__csm__'
#same temp vars are in: consumers.py, XC_CS_chat_master.py, XS_main_control.py
temp_CHAT_KEY = 'iMVUI1-4e-U_Ejr_mWwX-RdR5dz4ECb1'
temp_CHAT_IV = 'ZTvhkBXAV91Fi^3r'
#------
chat_key = mark_safe(json.dumps(os.environ.get('CHAT_KEY', temp_CHAT_KEY)))
chat_iv = mark_safe(json.dumps(os.environ.get('CHAT_IV', temp_CHAT_IV)))
chat_ready = bool(os.environ.get('CHAT_READY', cs_chat_ready_def))          #CHANGE TO CS_CHAT_READY
room_cs_master = mark_safe(json.dumps(os.environ.get('ROOM_CS_MASTER', temp_ROOM_CS_MASTER)))
room_otp = mark_safe(os.environ.get('ROOM_OTP', temp_ROOM_OTP))

def index(request):
    todaytag = str(datetime.date.today())
    ct = WebCounter(datestr=todaytag) if not WebCounter.objects.filter(datestr=todaytag) else WebCounter.objects.get(datestr=todaytag)
    ct.counts += 1
    ct.save()
    latest_article_list = Article.objects.filter(display=True,contributor_author=None).order_by('-pub_date')[:20]
    context = {'latest_article_list': latest_article_list, 'categories':Category.objects.all(), 'chat_ready':chat_ready,'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv}

    return render(request,'blog_t/index.html',context)

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
            return render(request,'blog_t/article_detail.html',{'article':article,'comments':comments, 'images':images,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv,'add_comment_form':Add_Comment()})
    else:
        add_comment = Add_Comment()
    return render(request,'blog_t/article_detail.html',{'article':article,'comments':comments, 'images':images,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv,'add_comment_form':add_comment})

def category_list(request,category_label):
    category = get_object_or_404(Category,category_label=category_label)
    articles = Category.objects.get(category_label=category_label).article_set.filter(display=True)
    return render(request,'blog_t/article_list.html',{'header':category.category_label,'articles':articles,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})

def my_articles_list(request,username):
    articles = Article.objects.filter(contributor_author=User.objects.get(username=username))
    return render(request,'blog_t/article_list.html',{'header':'My Article','articles':articles,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})

def upload_image(request,username):
    articles = Article.objects.filter(contributor_author=User.objects.get(username=username))
    if request.method == 'POST':
        form = Image_Form(request.POST, request.FILES)
        if form.is_valid():
            article = Article.objects.get(id = form.cleaned_data['article'].id)
            if article in articles or User.objects.get(username=username) in User.objects.filter(is_staff=True):
                """
                imgf= form.cleaned_data['img_file'].read()
                image_data = base64.b64encode(imgf).decode()    #image data for sending out
                """
                newimage = article.image_set.create(caption = form.cleaned_data['caption'], img_file = form.cleaned_data['img_file'])
                newimage.save()
                return render(request,'messages.html',{'messages':['Image upload success.'],'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})
            else:
                return render(request,'messages.html',{'messages':['Please attach the image to any of your article.'],'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})
    else:
        form = Image_Form()
    return render(request,'blog_t/upload_image.html',{'form':form,'articles':articles,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})

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
            return render(request,'messages.html',{'messages':['Thank you for your contribution.','Your article will appear after it is approved.'],'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})
    else:
        form = Compose_Form()
    return render(request,'blog_t/compose.html',{'form':form,'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})

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
        image_format, image_data = r_image_data.split(';base64,')   #image data for sending out
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
            return render(request,'messages.html',{'messages':['Signature upload successful.'],'categories':Category.objects.all(), 'chat_ready':chat_ready, 'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv})
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
    t = get_template('blog_t/chat_room.html')
    html = t.render({'room_name': mark_safe(json.dumps(room_name)),'chat_key':chat_key,'chat_iv':chat_iv})
    return HttpResponse(html)    
    """ #cs_chat is better to launch from base.html using javascript
    scrp = '<script>window.open("https://lkestories.herokuapp.com/chat/'+room_name+'/", "_blank", "toolbar=no,scrollbars=yes,resizable=yes,top=500,left=500,width=750,height=400")</script>'
    return HttpResponse(scrp)
    """

@staff_member_required()
def cs_chat_monitor(request,username):
    return render(request,'blog_t/cs_chat_monitor.html',{'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv,'username':mark_safe(json.dumps(username))})

def cs_chat_room(request,room_name,username,title):
    if chat_ready:
        return render(request,'blog_t/cs_chat_room.html',{'roomCSM':room_cs_master,'chat_key':chat_key,'chat_iv':chat_iv,'username':mark_safe(json.dumps(username)),'room_name': mark_safe(json.dumps(room_name)),'title':title+(('@'+room_name) if 'Chat Room' not in title else '')})
    else:
        raise Http404()

def send_OTP(request,message):
    print('get_current_site dir: ',dir(get_current_site(request)))  #TO BE DELETED
    print('get_current_site name: ',get_current_site(request).name)  #TO BE DELETED

    try:
        wsObj
    except NameError:
        wsObj = wscomm(get_current_site(request).domain,room_otp)
    message = '~01'+message
    result,attempt = '',1
    success = wsObj.sendWS(message,chat_key,chat_iv)
    if success[0]:
        while result!='S' and attempt<=max_attempt:
            result = wsObj.receive(chat_key,chat_iv)
            print('RESULT:{}. Attempt:{}'.format(result,attempt))
            attempt+=1
        return render(request,'messages.html',{'messages':['OTP sent to '+message[3:] if result=='S' else 'OTP sending unsuccessful. Please retry.']})
    else:
        return render(request,'messages.html',{'messages':['OTP sending unsuccessful. Please retry.']})

def enter_OTP(request,mobileno,message):
    try:
        wsObj
    except NameError:
        wsObj = wscomm(get_current_site(request).domain,room_otp)
    message = '~02'+mobileno+'|'+message
    wsObj.sendWS(message,chat_key,chat_iv)
    result,attempt = '',1
    while result not in ['Y','N'] and attempt<=max_attempt:
        success,result = wsObj.receive(chat_key,chat_iv)
        print('RESULT:{}. Attempt:{}'.format(result,attempt))
        attempt+=1
    status = 'OTP verification unsuccessful. Please retry.'
    if success[0]:
        if result=='Y':
            status = 'OTP verified'
        elif result=='N':
            status = 'OTP or mobile number did not match'
    return render(request,'messages.html',{'messages':[status]})