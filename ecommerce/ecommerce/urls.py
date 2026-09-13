"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from store.views import * 
from django.conf.urls.static import static
from django.conf import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',store,name="store"),
    path('product/<int:pk>/',productDetail,name="product_detail"),
    path('cart/',cart,name="cart"),
    path('checkout/',checkout,name="checkout"),
    path('login/',loginPage,name="login"),
    path('logout/',logoutUser,name="logout"),
    path('register/',registerPage,name="register"),
    path('update_item/',updateItem, name="update_item"),
    path('process_order/',processOrder,name="process_order")

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)