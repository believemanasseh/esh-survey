"""esh-survey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg2 import openapi
from drf_yasg2.views import SwaggerUIRenderer, get_schema_view
from rest_framework.permissions import AllowAny
from main.views import survey, webhook

SwaggerUIRenderer.template = 'swagger-ui.html'

schema_view = get_schema_view(
   openapi.Info(
      title="ESH Survey API",
      default_version='v1',
      description="Backend as a Service (BaaS) for ESH Survey",
   	  contact=openapi.Contact(email="esh-survey@email.com"),
   ),
   public=True,
   permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<int:survey_id>/<str:uuid>', survey, name='survey'),
    path('webhook', webhook, name="webhook"),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)