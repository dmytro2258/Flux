from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category, Order, OrderItem
from .cart import Cart

def home(request):
    products = Product.objects.all()
    context = {'products':products,}
    return render(request, "flux/index.html", context)


def checkout(request):
    cart = Cart(request)
    if len(cart) ==0:
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
        
        order = Order.objects.create(
            first_name = first_name,
            last_name = last_name,
            email=email,
            mobile=mobile,
            address=address,
            city=city,
            country=country,
            zip_code=zip_code,
            note=note
        )
        
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
        
        return render(request, 'flux/success.html')
    
    
    context = {
        "cart" :cart
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