from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import *
from .serializers import *
import uuid
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User created successfully',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.profile.full_name if hasattr(user, 'profile') else user.username,
                    'phone_number': user.profile.phone_number if hasattr(user, 'profile') else '',
                    'address': user.profile.address if hasattr(user, 'profile') else '',
                    'is_staff': user.is_staff
                },
                'token': token.key,
                'message': 'Login successful'
            })
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # ADD THIS ACTION FOR PASSWORD CHANGE
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password length
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    
    # ADD THIS ACTION FOR UPDATING PROFILE
    @action(detail=True, methods=['patch'])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        
        # Update User model fields
        if 'username' in request.data:
            user.username = request.data['username']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        
        # Update UserProfile fields
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        if 'full_name' in request.data:
            profile.full_name = request.data['full_name']
        if 'phone_number' in request.data:
            profile.phone_number = request.data['phone_number']
        if 'address' in request.data:
            profile.address = request.data['address']
        profile.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': profile.full_name,
                'phone_number': profile.phone_number,
                'address': profile.address,
                'is_staff': user.is_staff
            }
        })

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(status=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            products = Product.objects.filter(category_id=category_id, status=True)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'category_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            products = Product.objects.filter(
                Q(product_name__icontains=query) | Q(description__icontains=query),
                status=True
            )
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response([])

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.utils import timezone
        # Delete expired cart items automatically
        Cart.objects.filter(expires_at__lt=timezone.now()).delete()
        return Cart.objects.filter(user=self.request.user, status='active')
    
    queryset = Cart.objects.none()
    
    def create(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(product_id=product_id)
            
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                status='active',
                defaults={
                    'quantity': quantity,
                    'price': product.price
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        Cart.objects.filter(user=request.user, status='active').delete()
        return Response({'message': 'Cart cleared successfully'})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    queryset = Order.objects.none()
    
    def create(self, request):
        data = request.data.copy()
        data['order_number'] = str(uuid.uuid4())[:8].upper()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            order = serializer.save()
            
            product = order.product
            product.stock -= order.quantity
            product.sold_count += order.quantity
            product.save()
            
            Cart.objects.filter(user=request.user, status='active').delete()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    queryset = Payment.objects.none()

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [AllowAny]

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    # ✅ Only show messages related to logged-in user
    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).order_by('-created_at')

    # ✅ Create message
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['sender'] = request.user.id

        receiver_id = data.get('receiver')

        # 👉 If no receiver → send to admin
        if not receiver_id:
            admin_user = User.objects.filter(is_staff=True).first()

            if not admin_user:
                return Response(
                    {'error': 'No admin user found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data['receiver'] = admin_user.id

        # ✅ Validate and save
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ✅ Mark message as read
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()

        # 🔒 Only receiver can mark as read
        if message.receiver != request.user:
            return Response(
                {'error': 'Not allowed'},
                status=status.HTTP_403_FORBIDDEN
            )

        message.is_read = True
        message.save()

        return Response({'message': 'Message marked as read'})
# ============ ADMIN DASHBOARD VIEW ============
# Place this HERE - after all ViewSets, before the end of file
@staff_member_required
def admin_dashboard(request):
    context = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_products': Product.objects.count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
        'total_users': User.objects.count(),
        'unread_messages': Message.objects.filter(is_read=False).count(),
        'recent_orders': Order.objects.order_by('-created_at')[:10],
        'recent_messages': Message.objects.order_by('-created_at')[:10],
    }
    return render(request, 'admin/dashboard.html', context)
