from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas  # Pour générer le fichier PDF
from .models import Product, Order, Cart, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter


# import moncashify
# Create your views here.

def home(request):
    products = Product.objects.all()[:6]  # Récupère tous les produits
    return render(request, 'shop/index.html', {'products': products})

@login_required
def get_cart_content(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_html = render_to_string('shop/cart_items.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
    return JsonResponse({'html': cart_html})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Vérifie si le produit est déjà dans le panier
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1  # Incrémente la quantité si déjà présent
    cart_item.save()
    messages.success(request, f'{product.name} has been added to your cart, look in the cart.')
    return redirect('/')    

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()  # Supprime l'article du panier

    # Si tu utilises une requête AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Sinon, redirige l'utilisateur vers la vue du panier
    return redirect('/')    

@login_required
def place_order(request, product_id):
    # Récupérer le produit en question
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Récupérer la quantité depuis le formulaire ou utiliser 1 comme valeur par défaut
        quantity = int(request.POST.get('quantity', 1))

        # Créer une commande pour l'utilisateur
        order = Order.objects.create(user=request.user)

        # Ajouter le produit à la commande via OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
        )

        # Calculer le total de la commande
        order.calculate_total()

        # Rediriger vers la page de confirmation
        return redirect('order_confirmation', order_id=order.id)

    # Si ce n'est pas un POST, afficher le formulaire avec le produit
    random_products = Product.objects.exclude(id=product_id).order_by('?')[:8]  # Suggestions de produits
    return render(request, 'shop/place_order.html', {'product': product, 'random_products': random_products})


@login_required
def order_from_cart(request):
    cart_items = Cart.objects.filter(user=request.user,order__isnull=True)

    if not cart_items.exists():
        return redirect('/')  # Rediriger si le panier est vide

    # Créer une commande
    
    order = Order.objects.create(user=request.user)

    # Ajouter les articles du panier à la commande
    total=0
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            total_price=cart_item.total_price,
        )
        total += cart_item.total_price
    order.total_price = total
    order.save()     

    # Supprimer les articles du panier
    cart_item.delete()

    # Rediriger vers la confirmation
    return redirect('order_confirmation', order_id=order.id)    
    

def order_confirmation(request, order_id):
    order = get_object_or_404(Order,id=order_id)
    order_items = order.order_items.all()
    total_order_price = sum(item.total_price for item in order_items)
    return render(request, 'shop/order_confirmation.html', {'order': order,'order_items': order_items,'total_order_price': total_order_price,})


def download_order_pdf(request, order_id):
    # Récupérer la commande
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.all()  # Récupère les OrderItems associés
    total_order_price = sum(item.total_price for item in order_items)

    # Générer le PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y_position = height - 100  # Position initiale

    def add_new_page():
        nonlocal y_position
        p.showPage()
        y_position = height - 100
        p.setFont("Helvetica", 12)

    # En-tête du PDF
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, y_position, f"Order Confirmation for {order.user.username}")
    y_position -= 20
    p.setFont("Helvetica", 12)
    p.drawString(margin, y_position, f"Date: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
    y_position -= 20
    p.drawString(margin, y_position, f"Order Code: {order.order_code}")
    y_position -= 30

    # Détails des produits
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y_position, "Product")
    p.drawString(margin + 200, y_position, "Quantity")
    p.drawString(margin + 300, y_position, "Price")
    p.drawString(margin + 400, y_position, "Total")
    y_position -= 10
    p.line(margin, y_position, width - margin, y_position)
    y_position -= 20

    p.setFont("Helvetica", 12)
    for item in order_items:
        if y_position < margin:  # Si on atteint la fin de la page
            add_new_page()
        p.drawString(margin, y_position, item.product.name)
        p.drawString(margin + 200, y_position, str(item.quantity))
        p.drawString(margin + 300, y_position, f"${item.product.price:.2f}")
        p.drawString(margin + 400, y_position, f"${item.total_price:.2f}")
        y_position -= 20

    # Ajouter le total de la commande
    if y_position < margin:  # Si on atteint la fin de la page
        add_new_page()
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y_position - 20, f"Total Order Price: ${total_order_price:.2f}")

    # Finalisation
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='order_summary.pdf')
@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')  # Commandes de l'utilisateur
    return render(request, 'shop/view_orders.html', {'orders': orders})



def custom_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('/')

def product_list(request):
    # Récupérer le terme de recherche depuis la barre de recherche
    query = request.GET.get('q', '')  # Si aucun terme n'est fourni, utiliser une chaîne vide
    if query:
        # Filtrer les produits par nom ou description
        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query) 
    else:
        # Afficher tous les produits si aucun terme n'est recherché
        products = Product.objects.all()

    return render(request, 'shop/product_list.html', {'products': products, 'query': query})   


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige vers la page de connexion après l'inscription
    else:
        form = CustomUserCreationForm()
    return render(request, 'shop/signup.html', {'form': form}) 

      











def custom_404(request, exception):
    return render(request, 'shop/404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    return render(request, '400.html', status=400)