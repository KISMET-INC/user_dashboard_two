from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.template import Context, loader
from django import template
from django.template.response import TemplateResponse
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
import bcrypt
from .forms import *
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import _thread

#=============================================##
# process_register()
#=============================================##
def process_register(request):
    post = request.POST
    errors = User.objects.basic_validator(post)


    if len(errors) > 0:
        for value in errors.values():
            messages.error(request,value)
        return redirect('/register')

    else :
        hash = bcrypt.hashpw(post['pass'].encode(), bcrypt.gensalt()).decode()
        user_level = 0

        users = User.objects.all()
        if len(users) < 1:
            user_level = 9


        new_user = User.objects.create(user_name=post['first'], password = hash, email = post['email'], user_level= user_level)

        if new_user.user_level == 9:
            return redirect('/explore/admin')

        if new_user.user_level != 9:
            kristen = User.objects.get(id=2)
            new_user.is_following.add(kristen)
            kristen.being_followed.add(new_user)
            new_user.being_followed.add(kristen)
            kristen.save()
            new_user.save()

        if user_level not in request.session:
            request.session['user_id'] = new_user.id
            request.session['user_name'] = new_user.user_name
            request.session['user_level'] = new_user.user_level
            send_email(session_user = new_user, action = 'REGISTERED')

            return redirect(f'/explore')

        return redirect(f'/explore')

#=============================================##
# process_signin()
#=============================================##
def process_signin(request):
    user = User.objects.filter(email = request.POST['email'])
    errors = User.objects.basic_validator_login(request.POST)

    if len(errors) > 0:
        for value in errors.values():
            messages.error(request,value)
        return redirect('/signin')

    else:
            this_user = User.objects.get(id = user[0].id)
            request.session['user_id'] = this_user.id
            request.session['user_name'] = this_user.user_name
            request.session['user_level'] = this_user.user_level
            send_email(session_user = this_user, action = 'SIGNED IN')

            if this_user.user_level == 9:
                return redirect('explore/admin')
            return redirect(f'/explore')


#=============================================##
# logout()
#=============================================##
def logout(request):
    request.session.flush()
    return redirect('/signin')



#=============================================##
# home()
#=============================================##
def landing(request):
    return render(request,'landing.html')

#=============================================##
# signin()
#=============================================##
def signin(request):
    return render(request,'signin.html')

#=============================================##
# register()
#=============================================##
def register(request):
    return render(request,'register.html')

#=============================================##
# admin()
#=============================================##
def admin(request):
    context = {
        'users': User.objects.all()
    }
    return render(request,'admin.html',context)


#=============================================##
# welcome-testers()
#=============================================##
def welcome_testers(request):
    return render(request, 'welcome_testers.html')


#=============================================##
# explore()
#=============================================##
def explore(request):

    if 'user_id' not in request.session:
        return redirect('/signin')
    
    if 'loads' not in request.session:
        request.session['loads'] = 12
    if 'page_num' not in request.session:
        request.session['page_num'] = 1

    print(request.session['loads'])
    print(request.session['page_num'])
    current_user = User.objects.get(id=request.session['user_id'])

    image_list = Image.objects.order_by("-created_at")
    page = request.GET.get('page',request.session['page_num'])

    paginator = Paginator(image_list, request.session['loads'])
    try:
        images2 = paginator.page(page)
    except PageNotAnInteger:
        images2 = paginator.page(1)
    except EmptyPage:
        images2 = paginator.page(paginator.num_pages)


    context = {
        'session_user': current_user,
        'users' : User.objects.all(),
        'images' : Image.objects.order_by("-created_at"),
        'location': 'explore',
        'icon': 'fas fa-cloud-upload-alt',
        'title': 'Share',
        'images2': images2,
    }


    if 'counter' not in request.session:
        request.session['counter'] = 0
    else :
        request.session['counter'] += 1

    if request.session['user_level'] == 0:
        return render(request,'explore.html',context)
    return render(request,'admin.html',context)


#=============================================##
# profile()
#=============================================##
def profile(request, user_id):
    session_user = User.objects.get(id=request.session['user_id'])
    images = Image.objects.filter(user = user_id).order_by("-created_at");

    heart_sum = 0
    for image in images:
        heart_sum += image.loves.count()

    context = {
        'upload_pet_form': UploadPetForm(),
        'session_user': session_user,
        'clicked_user' : User.objects.get(id=user_id),
        'images': images,
        'heart_sum': heart_sum,
    }
    return render(request,'profile.html',context)

#=============================================##
# edit_user() VIEW
#=============================================##
def edit_user(request,user_id):
    context = {
        'session_user' : User.objects.get(id=request.session['user_id']),
        'user_upload_img' : UploadUserImgForm(),
    }
    return render(request,'edit_user.html',context)


#=============================================##
# process_edit_user()
#=============================================##
def process_edit_user(request):

    errors = User.objects.basic_validator_edit_user(request.POST)

    if len(errors) > 0:
        for value in errors.values():
            messages.error(request,value)
        return redirect(f'/edit_user/{request.session["user_id"]}')
    else:
        session_user = User.objects.get(id=request.session['user_id'])
        user_upload_img = UploadUserImgForm(request.POST, request.FILES)

        session_user.email = request.POST['email']
        session_user.user_name = request.POST['user_name']

        if request.FILES:
            session_user.user_img = request.FILES['user_img']
        session_user.save()

        return redirect(f'/profile/{session_user.id}')

#=============================================##
# process_edit_user()
#=============================================##
def process_admin_edit_user(request,user_id):

    errors = User.objects.basic_validator_edit_user(request.POST)
    if len(errors) > 1:
        for value in errors.values():
            messages.error(request,value)
        return redirect(f'/admin_edit_user/{user_id}/0/0')
    else:
        clicked_user = User.objects.get(id=user_id)
        user_upload_img = UploadUserImgForm(request.POST, request.FILES)

        clicked_user.email = request.POST['email']
        clicked_user.user_name = request.POST['user_name']

        hash = bcrypt.hashpw(request.POST['pass'].encode(), bcrypt.gensalt()).decode()
        clicked_user.password = hash

        if request.FILES:
            clicked_user.user_img = request.FILES['user_img']
        
        clicked_user.save()

    return redirect(f'/explore/admin')


#=============================================##
# admin_edit_user() VIEW
#=============================================##
def admin_edit_user(request,user_id,image_id,modal_trigger):
    if image_id != 0:
        image = Image.objects.get(id=image_id)
    else:
        image = image_id

    context = {
        'session_user' : User.objects.get(id=request.session['user_id']),
        'image': image,
        'trigger': modal_trigger,
        'clicked_user' : User.objects.get(id=user_id),
        'user_upload_img' : UploadUserImgForm(),
        'location': 'admin_edit_user',

    }
    return render(request,'admin_edit_user.html',context)




#=============================================##
# process_admin_remove_user()
#=============================================##
def process_remove_user(request, user_id):
    this_user = User.objects.get(id = user_id)
    this_user.delete()
    return redirect('/explore/0')



#=============================================##
# bulletin()
#=============================================##
def bulletin(request,user_id,image_id, modal_trigger):
    if image_id != 0:
        current_image = Image.objects.get(id=image_id)
    else:
        current_image = 0;

    context = {
        'session_user': User.objects.get(id=request.session['user_id']),
        'selected_user': User.objects.get(id=user_id),
        'url' : f'/user/bulletin/{user_id}/{image_id}',
        'image': current_image,
        'images': Image.objects.order_by("-created_at"),
        'users': User.objects.all(),
        'comments': Comment.objects.filter(image = current_image).order_by('-created_at'),
    }
    return render(request,'bulletin.html',context)


#=============================================##
# edit_pet VIEW()
#=============================================##
def edit_image(request,image_id):
    context = {
        'image': Image.objects.get(id=image_id),
        'session_user': User.objects.get(id=request.session['user_id']),
    }
    return render(request,'edit_image.html', context)


#=============================================##
# process_add_pet_image()
# return redirect('/')
#=============================================##
def process_add_pet_image(request):

    errors = Image.objects.basic_validator_add_pet(request.POST, request.FILES)

    if len(errors) > 0:
        for value in errors.values():
            messages.error(request,value)
        return redirect(f'/profile/{request.session["user_id"]}')

    upload_pet_form = UploadPetForm(request.POST, request.FILES)
    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.create(pet_img = request.FILES['pet_img'], user = session_user, name = request.POST['name'], desc = request.POST['desc'] )
    this_image.save()
    send_email(session_user = session_user, action = 'SHARED', image = this_image)

    return redirect (f'/profile/{session_user.id}')


#=============================================##
# process_remove_pet_image()
#=============================================##
def process_remove_image(request,image_id):
    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=image_id)
    this_user = User.objects.get(id = this_image.user.id)
    this_image.delete()
    if session_user.user_level == 9:
        return redirect (f'/admin_edit_user/{this_user.id}')
    return redirect (f'/profile/{session_user.id}')

#=============================================##
# process_edit_image()
#=============================================##
def process_edit_image(request):
    errors = Image.objects.basic_validator_edit_pet(request.POST)
    if len(errors) > 0:
        for value in errors.values():
            messages.error(request,value)
        return redirect(f'/edit_image/{request.POST["image_id"]}')

    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=request.POST['image_id'])
    this_image.desc = request.POST['text']
    this_image.name = request.POST['name']
    this_image.save()
    # if session_user.user_level == 9:
    #     return redirect (f'/admin_edit_user/{this_user.id}')
    return redirect (f'/profile/{session_user.id}')

#=============================================##
# process_add_comment()
#=============================================##
def process_add_comment(request):
    errors = Image.objects.basic_validator_add_comment(request.POST)
    session_user = User.objects.get(id= request.session['user_id'])
    this_image = Image.objects.get(id = request.POST['image_id'])
    if len(errors) < 1:
        new_comment = Comment.objects.create(text = request.POST['text'], image = this_image, user= session_user)
        send_email(session_user = session_user, action = 'COMMENTED', clicked_user = this_image.user, image = this_image, comment=new_comment)

    context = {
        'image': this_image,
        'session_user': session_user
    }
        #hidden form field
    if request.POST['component'] == 'from_post':
        return redirect(f'/replace_post/{this_image.id}')
    return redirect( f'/replace_comments/{this_image.id}')


#=============================================##
# process_delete_comment()
#=============================================##
def process_delete_comment(request,comment_id,component):
    session_user = User.objects.get(id= request.session['user_id'])
    this_comment = Comment.objects.get(id = comment_id)
    image_id = this_comment.image.id
    clicked_user = this_comment.user
    this_comment.delete();
    if component == 'from_post':
        return redirect(f'/replace_post/{image_id}')
    return redirect(f'/replace_comments/{image_id}')

#=============================================##
# replace_comments()
#=============================================##
def replace_comments(request, image_id):
    session_user = User.objects.get(id= request.session['user_id'])
    this_image = Image.objects.get(id = image_id)
    context = {
        'image': this_image,
        'session_user': session_user
    }
    return render(request, 'modules/modal_comments.html', context)


#=============================================##
# replace_post()
#=============================================##
def replace_post(request, image_id):
    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=image_id)
    context = {
        'image': this_image,
        'session_user': session_user
    }
    return render(request,'modules/post.html', context)

#=============================================##
# replace_modal()
#=============================================##
def replace_modal(request, image_id):
    context = {
        'image' : Image.objects.get(id=image_id),
        'session_user' : User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'modules/modal.html', context)

#=============================================##
# get_heart_sum()
#=============================================##
def get_heart_sum(request,image_id):
    image = Image.objects.get(id=image_id)
    user = image.user
    sum = 0
    for image in user.images.all():
        sum+=len(image.loves.all())

    return HttpResponse (sum);

#=============================================##
# process_heart()
#=============================================##
def process_heart(request,image_id,location):

    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=image_id)

    if session_user in this_image.loves.all():
        this_image.loves.remove(session_user)
    else:
        send_email(session_user = session_user, action = 'LOVED', clicked_user = this_image.user, image = this_image)
        this_image.loves.add(session_user)

    this_image.save();
    if location == 'bulletin':
        return redirect(f'/replace_post/{this_image.id}')

    return redirect(f'/replace_stats/{this_image.id}')


#=============================================##
# replace stats
#=============================================##
def replace_stats(request, image_id):
    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=image_id)
    context = {
        'image': this_image,
        'session_user': session_user
    }
    return render(request,'modules/stats.html', context)

#=============================================##
# replace stats
#=============================================##
def get_image_list(request, user_id):
    user_images = User.objects.get(id=user_id).images.all()
    image_list = []
    for image in user_images:
        image_list.append(image.id)

    return JsonResponse ({'images': image_list})


#=============================================##
# replace image
#=============================================##
def replace_image(request, image_id):
    session_user = User.objects.get(id=request.session['user_id'])
    this_image = Image.objects.get(id=image_id)
    context = {
        'image': this_image,
        'session_user': session_user
    }
    return render(request,'modules/image.html', context)


#=============================================##
# process_follow()
# return redirect('/')
#=============================================##
def process_follow(request,user_to_follow_id,image_id):
    session_user = User.objects.get(id= request.session['user_id'])
    user_to_follow = User.objects.get(id= user_to_follow_id)
    send_email(user_to_follow,'follow')

    if user_to_follow not in session_user.is_following.all():
        session_user.is_following.add(user_to_follow)
        user_to_follow.being_followed.add(session_user)
    else:
        session_user.is_following.remove(user_to_follow)
        user_to_follow.being_followed.remove(session_user)

    session_user.save()
    user_to_follow.save()

    if image_id == '0':
        return redirect(f'/profile/{user_to_follow_id}')

    return redirect (f'/replace_stats/{user_to_follow.id}')



#=============================================##
# get_session_id()
#=============================================##
def get_session_id(request):
    session_user = User.objects.get(id= request.session['user_id'])
    return JsonResponse ({'session_id': session_user.id, 'session_user_name' :session_user.user_name})

#=============================================##
# get_more_images()
#=============================================##
def get_more_images(request):
    request.session['page_num'] += 1
    image_list = Image.objects.order_by("-created_at")
    page = request.GET.get('page',request.session['page_num'])
    paginator = Paginator(image_list,request.session['loads'])
    request.session['loads'] += 12

    print(request.session['loads'])
    print(request.session['page_num'])

    try:
        images2 = paginator.page(page)
    except PageNotAnInteger:
        images2 = paginator.page(1)
    except EmptyPage:
        images2 = paginator.page(paginator.num_pages)
        return HttpResponse("none")

    return render(request, 'modules/dashboard.html', {'images2': images2, 'session_user' : User.objects.get(id=request.session['user_id'])})

#=============================================##
# search users
#=============================================##
def search(request):
    print(request.POST)
    user_search = User.objects.filter(email=request.POST['user_email'])
    
    if len(user_search) > 0 :
        find_user = user_search[0]
        return HttpResponse(f'/profile/{find_user.id}')
        
    return HttpResponse(None)


def get_followers_list(request):
    context = {
        'users': User.objects.get(id=request.session['user_id']).being_followed.all(),
    }
    print(context['users'])
    return render(request, 'modules/followers_modal.html', context)

def get_all_users_list(request):
    context = {
        'users': User.objects.all()
    }
    return render(request, 'modules/users_modal.html', context)
#=============================================##
# send _email()
#=============================================##
def send_email(session_user, action, clicked_user = None, image = None, comment = None):

    html_body = ""
    text_body = ""
    subject = action
    def img_info(text_body):
        string = """ <h2>""" + text_body + """ </h2>
        <p> Name:""" + image.name +""" </p>
        <p> Image ID:  """ + str(image.id) + """ </p>
        <a href = http://localhost:8000""" + image.pet_img.url +  """>"""+ image.pet_img.url + """</a> """
        return string

    if action == 'LOVED':
        text_body =  f"{session_user.user_name} LOVED {clicked_user.user_name}'s image!"
        html_body =  img_info(text_body)

    if action == 'COMMENTED':
        text_body =  f"{session_user.user_name} COMMENTED ON {clicked_user.user_name}'s image!"
        html_body =  img_info(text_body) + """
        <p><b> """ + session_user.user_name +"""</b> said ' """ + comment.text + """ '</p>
        """

    if action =='SIGNED IN':
        text_body =  f"{session_user.user_name} SIGNED IN!"
        html_body =  """
        <h2>""" + text_body + """ </h2>
        """
    if action =='REGISTERED':
        text_body =  f"{session_user.user_name} REGISTERED A NEW ACCOUNT!"
        html_body =  """
        <h2>""" + text_body + """ </h2>
        """

    if action =='SHARED':
        text_body =  f"{session_user.user_name} SHARED A PET!"
        html_body =  """
        <h2>""" + text_body + """ </h2>
        <p> Name:""" + image.name +""" </p>
        <p> Image ID:  """ + str(image.id) + """ </p>
        <p> """ + image.pet_img.url +  """</p>
        """

    def setup_email_thread():

        smtp_server = "smtp.gmail.com"
        port = 587 #For starttls
        password = 'PassioN12345'

        sender_email = "petsconnect2021@gmail.com"
        receiver_email = "petsconnect2021@gmail.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        text = """\
            """ + text_body

        html = """\
        <html>
        <body>
        """ + html_body + """
        </body>
        </html>
        """

        # Convert message types into MIMETEXT
        part1 = MIMEText(text,'plain')
        part2 = MIMEText(html, 'html')

        # Attach to message object
        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)

        server.starttls(context = context) #Secure the connection
        server.login (sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
     
    try:
        # Create new thread
        _thread.start_new_thread(setup_email_thread,())

    except Exception as e:
        print("error sending email")





#=============================================##
# process_edit_password()
# NOT BEING USED YET
#=============================================##
def process_edit_password(request):
    errors = User.objects.basic_validator_passwords(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f'/edit_user/{request.POST["user_id"]}')
    else:
        session_user = User.objects.get(id=request.POST['user_id'])
        session_user.password = request.POST['pass']


    return redirect(f'/edit_user/{session_user.id}')
