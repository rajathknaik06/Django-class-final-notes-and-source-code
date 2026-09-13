from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder


def ensure_customer(user):
	customer, _ = Customer.objects.get_or_create(
		user=user,
		defaults={
			'name': user.get_full_name() or user.username,
			'email': user.email or f'{user.username}@example.com',
		},
	)
	return customer


def loginPage(request):
	if request.user.is_authenticated:
		return redirect('store')

	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			ensure_customer(user)
			return redirect('store')
		messages.error(request, 'Invalid username or password.')

	return render(request, 'store/login.html')


def logoutUser(request):
	logout(request)
	return redirect('store')


def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')

	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip()
		password = request.POST.get('password', '')
		password2 = request.POST.get('password2', '')

		if not username or not password:
			messages.error(request, 'Username and password are required.')
		elif password != password2:
			messages.error(request, 'Passwords do not match.')
		elif User.objects.filter(username=username).exists():
			messages.error(request, 'Username already taken.')
		else:
			user = User.objects.create_user(username=username, email=email, password=password)
			Customer.objects.create(
				user=user,
				name=username,
				email=email or f'{username}@example.com',
			)
			login(request, user)
			return redirect('store')

	return render(request, 'store/register.html')


def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def productDetail(request, pk):
	data = cartData(request)
	cartItems = data['cartItems']
	product = get_object_or_404(Product, id=pk)
	reviews = product.reviews.all().order_by('-date_added')

	if request.method == 'POST':
		rating = int(request.POST.get('rating', 5))
		comment = request.POST.get('comment', '').strip()
		name = request.POST.get('name', '').strip()

		if request.user.is_authenticated:
			customer = ensure_customer(request.user)
			name = name or customer.name or request.user.username
		else:
			customer = None
			name = name or 'Guest'

		if comment and 1 <= rating <= 5:
			Review.objects.create(
				product=product,
				customer=customer,
				name=name,
				rating=rating,
				comment=comment,
			)
			messages.success(request, 'Thanks for your review!')
			return redirect('product_detail', pk=product.id)
		messages.error(request, 'Please provide a rating and review comment.')

	context = {
		'product': product,
		'reviews': reviews,
		'cartItems': cartItems,
		'rating_range': range(1, 6),
	}
	return render(request, 'store/product_detail.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = ensure_customer(request.user)
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = ensure_customer(request.user)
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)