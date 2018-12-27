from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('blog.urls')),
    path('account/',include('django.contrib.auth.urls')),
    path('account/signup/', views.signup, name='signup'),
    path('account/reactivate/', views.reactivate, name='reactivate'),
    path('account/activate/<str:uidb64>/<str:token>', views.activate, name='activate'),

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
