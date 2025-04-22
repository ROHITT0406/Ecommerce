from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .models import Product,Cart,Order,Address,Orderdetails
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from collections import defaultdict
import uuid
from collections import OrderedDict
from django.utils.timezone import now
import stripe
from django.conf import settings
# Create your views here.


def cart_Quantity(cart_items):
    cart_quantity=0
    for item in cart_items:
        cart_quantity+=item.quantity
    return cart_quantity


def home(request):
    
    cart_quantity=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_quantity=cart_Quantity(cart_items)

    query=request.GET.get('search')
    if query:
        products=Product.objects.filter(Q(product_name__icontains=query) | Q(key_word__icontains=query)| 
        Q(product_count__icontains=query))
    else:
        products=Product.objects.all()
    return render(request,'index.html' ,{'products':products,'cart_quantity':cart_quantity})



def profile_view(request):
    user = request.user
    all_orders = Order.objects.filter(user=user).order_by('-order_date')
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.filter(user=user).first()

    cart_quantity = cart_Quantity(cart_items)


    return render(request, 'profile.html', {
        'user': user,
        # 'orders': unique_orders.values(),  # Only one order per order_id
        'address': address,
        'cart_quantity': cart_quantity,
    })
def add_address(request):
    cart_quantity=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_quantity=cart_Quantity(cart_items)
    if request.method == 'POST':
        full_name=request.POST.get('fname')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        zip_code=request.POST.get('zip')
        phone_number=request.POST.get('phone')

        address=Address.objects.create(user=request.user, full_name=full_name,street=street,city=city,state=state,zip_code=zip_code,phone_number=phone_number)
        address.save()
        return redirect('profile')
        
    return render(request,'address.html',{'cart_quantity':cart_quantity})

def edit_address(request):
    cart_quantity=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_quantity=cart_Quantity(cart_items)
    address=Address.objects.filter(user=request.user).first()
    if request.method == 'POST':
        address.street=request.POST.get('street')
        address.city=request.POST.get('city')
        address.state=request.POST.get('state')
        address.zip_code=request.POST.get('zip')
        address.phone_number=request.POST.get('phone')

        address.save()
        return redirect('profile')
    return render(request,'edit_address.html',{'cart_quantity':cart_quantity})


def remove_address(request):
    user=request.user
    Address.objects.get(user=user).delete()
    return redirect('profile')


def reset_password(request):
    cart_quantity=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_quantity=cart_Quantity(cart_items)
    if request.method == "POST":
        email=request.POST.get('email')
        new_password=request.POST.get('pass1')
        try:
            user=User.objects.get(username=email)
            user.set_password(new_password)
            user.save()
            messages.success(request,'password changed successfully')
        except User.DoesNotExist:
            messages.warning(request,'Email not found')
            return redirect('reset-password')
        return redirect('login')
    next_url = request.GET.get('next', 'login') 
    return render(request, 'resetpassword.html', {'next_url': next_url,'cart_quantity':cart_quantity})


def handlelogin(request):
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('pass1')
        user=authenticate(username=email,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.warning(request,"Invalid credentials")
            return redirect('login')

    return render(request,'login.html')


def handlesignup(request):
    if request.method == "POST":
        email=request.POST.get('email')
        fname=request.POST.get('fname')
        password=request.POST.get('pass1')
        confirmpass= request.POST.get('pass2')
        if len(password)!=6:
            messages.warning(request,"Password must be exactly 6 characters long ")
            return redirect("signup")
        if password != confirmpass:
            messages.warning(request,"Password is not matching")
            return redirect("signup")
      
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email already exist")
                return render(request,'signup.html')
        except Exception as identifier:
            pass
        user=User.objects.create_user(email,email,password,first_name=fname)
        user.save()
        return redirect('login')
    return render(request,'signup.html')


def handlelogout(request):
    logout(request)
    messages.success(request,"Logout successfully")
    return redirect("/")

stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required(login_url='/login/')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_quantity = cart_Quantity(cart_items)
    address = Address.objects.filter(user=request.user)

    # Display in INR
    total_price = sum(item.totalprice for item in cart_items)
    shipping_cost = 4.99  # INR
    total_before_tax = total_price + shipping_cost
    estimated_tax = round(total_before_tax * 0.10, 2)
    total_amount = round(total_before_tax + estimated_tax, 2)

    # Currency conversion only for Stripe
    # INR_TO_USD_RATE = 0.012
    line_items = []

    # Add cart items
    for item in cart_items:
        usd_price = item.product.product_price 
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.product_name,
                },
                'unit_amount': max(50, int(usd_price * 100)),
            },
            'quantity': item.quantity,
        })

    # Add shipping as line item
    shipping_cost_usd = shipping_cost 
    line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Shipping',
            },
            'unit_amount': max(50, int(shipping_cost_usd * 100)),
        },
        'quantity': 1,
    })

    # Add tax as line item
    estimated_tax_usd = estimated_tax 
    line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'GST (10%)',
            },
            'unit_amount': max(50, int(estimated_tax_usd * 100)),
        },
        'quantity': 1,
    })

    # Validate minimum total
    total_amount_usd = total_amount 
    if total_amount_usd < 0.50:
        return render(request, 'checkout.html', {
            'cart_item': cart_items,
            'total_price': total_price,
            'shipping_cost': shipping_cost,
            'estimated_tax': estimated_tax,
            'total_amount': total_amount,
            'cart_quantity': cart_quantity,
            'stripe_session_id': None,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'total_before_tax': total_before_tax,
            'address': address,
            'error': "Total is too low for Stripe ($0.50 minimum). Please add more items.",
        })

    # Create Stripe session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/place-order') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/checkout/'),
        customer_email=request.user.email,
    )

    # Final render
    return render(request, 'checkout.html', {
        'cart_item': cart_items,
        'total_price': total_price,
        'shipping_cost': shipping_cost,
        'estimated_tax': estimated_tax,
        'total_amount': total_amount,
        'cart_quantity': cart_quantity,
        'stripe_session_id': session.id,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'total_before_tax': total_before_tax,
        'address': address,
    })

def orders(request):
    cart_item=Cart.objects.filter(user=request.user)
    cart_quantity=cart_Quantity(cart_item)
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')
    
    # Grouping orders by 'order_id'
    grouped_orders = {}
    for order in orders:
        if order.order_id not in grouped_orders:
            grouped_orders[order.order_id] = {
                'order_date': order.order_date,
                'total_price': order.total_price,
                'items': []
            }
        grouped_orders[order.order_id]['items'].append(order)

    context = {'grouped_orders': grouped_orders,'cart_quantity':cart_quantity}
    return render(request,'orders.html',context)


def place_order(request):
    session_id = request.GET.get('session_id')
    print(session_id)
    if not session_id:
        messages.error(request, "Session ID missing.")
        return redirect('checkout')

    try:
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['payment_intent']
        )
    except Exception as e:
        messages.error(request, f"Stripe error: {str(e)}")
        return redirect('checkout')

    if session.payment_status == 'paid':
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            messages.warning(request, "No items found in cart.")
            return redirect('checkout')

        order_id = str(uuid.uuid4().hex[:10]).lower()

        order_date = timezone.now()
        total_amount = session.amount_total/100   # USD

        for item in cart_items:
            delivery_date = item.add_to_date + timedelta(days=3)

            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                total_price=total_amount,
                delivery_date=delivery_date,
                order_id=order_id,
                order_date=order_date
            )

        # ✅ Save order summary once
        Orderdetails.objects.create(
            name=user.username,
            amount=total_amount,
            order_id=order_id,
            razorpay_payment_id=session.payment_intent.id,
            paid=True
        )

        # ✅ Clear cart
        cart_items.delete()

        # messages.success(request, "✅ Payment successful and order placed!")
        return redirect('stripe-success')
    
    else:
        # messages.error(request, "❌ Payment failed.")
        return redirect('checkout')

def tracking(request,order_id):
    cart_quantity=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_quantity=cart_Quantity(cart_items)
    order_item=Order.objects.get(user=request.user,id=order_id)
    current_date = timezone.now().date()
    delivery_date = order_item.delivery_date.date()

    
    days_remaining = (delivery_date - current_date).days

    if days_remaining >= 2:
        current_status = "Preparing"
        progress = "33%"
    elif days_remaining == 1:
        current_status = "Shipped"
        progress = "66%"
    else:
        current_status = "Delivered"
        progress = "100%"
    return render(request,'tracking.html',{'cart_quantity':cart_quantity,'order_item':order_item,'current_status': current_status,
        'progress': progress})



@login_required(login_url='/login/')
def add_to_cart(request,product_id):
    if request.method == "POST":
        product=get_object_or_404(Product,id=product_id)
        quantity=int(request.POST.get('quantity',1))

        cart_item,created=Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity, 'add_to_date': timezone.now()}
        )

        if not created:
            cart_item.quantity+=quantity
            cart_item.save()
        
    next_url = request.POST.get('next', '/#products')
    return redirect(next_url)
   

def handledelete(request,product_id):
    if request.user.is_authenticated:
        cart_item=Cart.objects.filter(user=request.user,product__id=product_id).delete()
    return redirect('checkout')


def update(request, product_id, action):
    if request.method == "POST":
        try:
            cart_item = Cart.objects.get(user=request.user, product__id=product_id)
            
            if action == "increment":
                cart_item.quantity += 1
            elif action == "decrement":
                if cart_item.quantity >1: 
                    cart_item.quantity -= 1 

            cart_item.save()
        except Cart.DoesNotExist:
            pass
    return redirect('checkout')

def stripe_success(request):
    session_id = request.GET.get('session_id')
    # handle session logic here if needed
    return render(request, 'success.html', {'session_id': session_id})

def stripe_failure(request):
    session_id = request.GET.get('session_id')
    # handle session logic here if needed
    return render(request, 'failure.html', {'session_id': session_id})
def cancel_order(request, item_id):
    order_item = get_object_or_404(Order, id=item_id, user=request.user)
    if not order_item.is_cancelled:
        order_item.is_cancelled = True
        order_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'orders'))