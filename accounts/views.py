from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)
        user.save()
        # In production, send OTP via email/SMS
        print(f"OTP for {user.email}: {otp}")

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'user': UserProfileSerializer(serializer.validated_data['user']).data,
                'refresh': serializer.validated_data['refresh'],
                'access': serializer.validated_data['access'],
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email)
            if user.otp == otp and user.otp_expires_at > timezone.now():
                user.is_verified = True
                user.verified_at = timezone.now()
                user.otp = None
                user.otp_expires_at = None
                user.save()
                return Response({'message': 'Email verified successfully'})
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    class VendorRatingCreateView(generics.CreateAPIView):
    serializer_class = VendorRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class VendorRatingListView(generics.ListAPIView):
    serializer_class = VendorRatingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        return VendorRating.objects.filter(vendor_id=vendor_id, is_approved=True).order_by('-created_at')