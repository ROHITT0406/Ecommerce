from django.urls import path
from ecommerceapp import views

urlpatterns = [
     path('', views.home,name="home"),
     path('checkout/',views.checkout,name="checkout"),
     path('orders/',views.orders,name="orders"),
     path('tracking/<int:order_id>/',views.tracking,name="tracking"),
     path('profile/', views.profile_view, name='profile'),
     path('add-address/', views.add_address, name='address'),
     path('edit-address/', views.edit_address, name='edit-address'),
     path('reset-password/', views.reset_password, name='reset-password'),
     path('remove-address/', views.remove_address, name='remove-address'),



     path('login/',views.handlelogin,name="login"),
     path('signup/',views.handlesignup,name="signup"),
     path('logout/',views.handlelogout,name='logout'),

     path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
     path('delete/<int:product_id>/',views.handledelete,name='delete'),

     path('update/<int:product_id>/<str:action>/', views.update, name='update'),
     path('place-order',views.place_order,name='place-order'),
     path('stripe', views.stripe_success, name='stripe-success'),
     path('failure',views.stripe_failure,name='stripe-failure'),
    path('cancel-order/<int:item_id>/', views.cancel_order, name='cancel-order'),


]