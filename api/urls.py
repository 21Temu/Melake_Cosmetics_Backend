from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'cart', views.CartViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'banks', views.BankViewSet)
router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]