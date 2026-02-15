from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category, Order, OrderItem
from .cart import Cart
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q #complex search module
import qrcode
import base64
from io import BytesIO

def home(request):
    category_id = request.GET.get('category')
    products = Product.objects.all()
    categories = Category.objects.all()
    query = request.GET.get('q')
    
    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))   
        
    context = {'products':products,
               'categories': categories}
    
    return render(request, "flux/index.html", context)


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        zip_code = request.POST.get('zip_code')
        note = request.POST.get('note')
        shipping_method = request.POST.get('shipping_option')
        payment_method = request.POST.get('payment_method')
               
        
        shipping_cost = 0
        if shipping_method == 'Pickup':
            shipping_cost = 3.00
        elif shipping_method == "Standard":
            shipping_cost = 5.00
        elif shipping_method == "Local":
            shipping_cost = 1.00
            
        cart_total = float(cart.get_total_price())
        grand_total = cart_total + shipping_cost
        
        qr_code_base64 = None 
        
            
        if payment_method == "Direct Bank Transfer":
            iban = "CZ7406000000000264070125"
            qr_data = f"SPD*1.0*ACC:{iban}*AM:{grand_total:.2f}*CC:CZK*MSG:ElectroShopTest"
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        order = Order(
            first_name = first_name,
            last_name = last_name,
            email=email,
            mobile=mobile,
            address=address,
            city=city,
            country=country,
            zip_code=zip_code,
            note=note,
            shipping_method = shipping_method,
            shipping_cost = shipping_cost,
            payment_method = payment_method,
        )
        
        if request.user.is_authenticated:
            order.user = request.user
        
        order.save()
        
        for item in cart:
            product = item['product']
            quantity = int(item['quantity'])
            price = item['price']
            
            OrderItem.objects.create(
                order = order,
                product = product,
                price = price,
                quantity = quantity,
            )
        
        cart.clear()
        
        success_context = {
            "qr_code" : qr_code_base64,
            "grand_total" : grand_total
        }
        
        
        return render(request, 'flux/success.html', success_context)
    
    
    context = {
        "cart" :cart,
        
    }
    
    return render(request, "flux/checkout.html", context)  



def add_to_cart(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    quantity = request.POST.get('quantity', 1)
    cart.add(product=product, quantity=quantity)
    return redirect('home')
  
def cart(request):
    cart = Cart(request)
    context = {
        "cart": cart
    }
    
    return render(request, "flux/cart.html", context)



def cart_delete(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.delete(product=product)
    return redirect('cart')



def product_detail(request, pk):
    product = get_object_or_404(Product,pk=pk)
    categories = Category.objects.all()
    context= {
        'product' : product,
        'categories' : categories,
    }
    
    return render(request, "flux/single.html", context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
        
    context = {'form': form}
    return render(request, 'flux/signup.html', context)

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).filter(user=request.user).order_by('-created')
    context = {'orders': orders}
    return render(request, 'flux/user_orders.html', context)