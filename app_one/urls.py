from django.urls import path
from . import views
from django.contrib import admin 
from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static 
from .views import *


urlpatterns = [

    # path('',views.landing),

    path('', views.landing),
    path('register', views.register),
    path('signin', views.signin),
    path('process_register', views.process_register),
    path('process_signin', views.process_signin),
    path('logout', views.logout),



    path('profile/<int:user_id>/<int:image_id>/<int:modal_trigger>', views.profile),
    path('edit_user/<int:user_id>', views.edit_user),
    path('process_add_image', views.process_add_image),
    path('process_remove_image/<int:image_id>/<str:location>', views.process_remove_image),
    path('process_edit_user', views.process_edit_user),
    path('process_edit_password', views.process_edit_password),

    path('bulletin/<int:user_id>/<int:image_id>/<int:modal_trigger>', views.bulletin),
    path('explore/<int:user_id>/<int:image_id>/<int:modal_trigger>', views.explore),
    path('process_add_comment/<str:location>', views.process_add_comment),
    path('process_heart/<int:image_id>/<str:location>', views.process_heart),
    path('process_follow/<int:image_id>/<int:user_to_follow_id>/<str:location>', views.process_follow),
    
    path('explore/admin', views.admin),
    path('process_remove_user/<int:user_id>', views.process_remove_user),

    path('process_delete_comment/<int:comment_id>/<int:image_id>/<str:location>/<str:component>',views.process_delete_comment),
    path('stop_following/<int:user_id>',views.stop_following),

    path('updated_stats/<int:image_id>', views.updated_stats),
    path('updated_post/<int:image_id>', views.updated_post)
]
