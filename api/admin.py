from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html
from .models import *

# Customize admin site header and title
admin.site.site_header = "Melake Mihiret Admin Panel"
admin.site.site_title = "Admin Dashboard"
admin.site.index_title = "Welcome to Melake Mihiret Admin"

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone_number', 'address', 'status']
    list_filter = ['status']
    search_fields = ['full_name', 'phone_number', 'user__username', 'address']
    readonly_fields = ['user']
    fields = ['user', 'full_name', 'phone_number', 'address', 'status']
    
    # Optional: Add a method to show address truncated if too long
    def short_address(self, obj):
        if obj.address:
            return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
        return '-'
    short_address.short_description = 'Address'
# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'display_image', 'price', 'stock', 'status', 'sold_count']
    list_filter = ['status', 'category']
    search_fields = ['product_name', 'description']
    list_editable = ['price', 'stock', 'status']
    readonly_fields = ['sold_count', 'created_at']
    fields = [
        'product_name', 'description', 'category', 'price', 
        'stock', 'product_image', 'status', 'sold_count', 'created_at'
    ]
    
    actions = ['mark_as_available', 'mark_as_out_of_stock']
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f'{updated} products marked as available.')
    mark_as_available.short_description = "Mark selected products as Available"
    
    def mark_as_out_of_stock(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f'{updated} products marked as out of stock.')
    mark_as_out_of_stock.short_description = "Mark selected products as Out of Stock"
    
    def display_image(self, obj):
        if obj.product_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 8px;"/>', obj.product_image.url)
        return "-"
    display_image.short_description = 'Image'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'product_image_thumbnail', 'payment_proof_thumbnail', 'user', 'product_name', 'amount', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'product_name', 'name', 'phone_number']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    fields = [
        'order_number', 'user', 'product', 'product_name', 'name',
        'amount', 'quantity', 'address', 'phone_number', 'payment_image',
        'status', 'cancellation_reason', 'created_at'
    ]
    
    # Product image thumbnail
    def product_image_thumbnail(self, obj):
        if obj.product and obj.product.product_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.product.product_image.url
            )
        return format_html(
                '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px;">📦</div>'
            )
    product_image_thumbnail.short_description = 'Product'
    
    # Payment proof image thumbnail
    def payment_proof_thumbnail(self, obj):
        if obj.payment_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover; cursor: pointer;" /></a>',
                obj.payment_image.url,
                obj.payment_image.url
            )
        return format_html(
                '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:8px;display:flex;align-items:center;justify-content:center;">💳</div>'
            )
    payment_proof_thumbnail.short_description = 'Payment Proof'
    
    # Existing actions
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as Processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'product_image_thumbnail', 'payment_proof_thumbnail', 'user', 'product_name', 'amount', 'quantity', 'status', 'created_at']
    # Removed 'order_number_link' from list_display
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'product_name', 'name', 'phone_number']
    list_editable = ['status']
    readonly_fields = ['payment_id', 'created_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['status'].initial = 'completed'
        return form
    
    def product_image_thumbnail(self, obj):
        if obj.product and obj.product.product_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.product.product_image.url
            )
        elif obj.product_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.product_image.url
            )
        return format_html(
            '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px;">📷</div>'
        )
    product_image_thumbnail.short_description = 'Product Image'
    
    def payment_proof_thumbnail(self, obj):
        if obj.payment_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover; cursor: pointer; border: 1px solid #ddd;" /></a>',
                obj.payment_image.url,
                obj.payment_image.url
            )
        return format_html(
            '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:8px;display:flex;align-items:center;justify-content:center;">💳</div>'
        )
    payment_proof_thumbnail.short_description = 'Payment Proof'

class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'product_image_thumbnail', 'user', 'product', 'quantity', 'price', 'status', 'expires_at', 'is_expired']
    list_filter = ['status', 'expires_at']
    search_fields = ['user__username', 'product__product_name']
    
    def product_image_thumbnail(self, obj):
        if obj.product and obj.product.product_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.product.product_image.url
            )
        return format_html(
            '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:8px;display:flex;align-items:center;justify-content:center;">📷</div>'
        )
    product_image_thumbnail.short_description = 'Image'
    
    def is_expired(self, obj):
        from django.utils import timezone
        if obj.expires_at and obj.expires_at < timezone.now():
            return '⚠️ Expired'
        return '✓ Active'
    is_expired.short_description = 'Status'

# Bank Admin
class BankAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'account_number']
    search_fields = ['bank_name', 'account_number']

# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'sender', 'receiver', 'short_message', 'is_read', 'created_at', 'reply_button']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'message']
    list_editable = ['is_read']
    readonly_fields = ['reply_button']
    
    # ========== NEW: Redirect list view to chat dashboard ==========
    def changelist_view(self, request, extra_context=None):
        """Redirect the default message list to the chat dashboard"""
        return HttpResponseRedirect(reverse('admin:chat_dashboard'))
    
    # ========== NEW: Redirect add view to chat dashboard ==========
    def add_view(self, request, form_url='', extra_context=None):
        """Redirect the add message form to the chat dashboard"""
        return HttpResponseRedirect(reverse('admin:chat_dashboard'))
    # ========== END NEW ==========
    
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'
    
    def reply_button(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background: #417690; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">✉️ Reply</a>',
            reverse('admin:reply_to_message', args=[obj.message_id])
        )
    reply_button.short_description = 'Reply'

# Custom Admin Site with Reply Functionality
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('chat/', self.admin_view(self.chat_dashboard), name='chat_dashboard'),
            path('reply-to-message/<int:message_id>/', self.admin_view(self.reply_to_message), name='reply_to_message'),
        ]
        return custom_urls + urls
    
    def chat_dashboard(self, request):
        from django.shortcuts import render
        return render(request, 'admin/chat_dashboard.html', {
            'title': 'Message Center'
        })
    
    def reply_to_message(self, request, message_id):
        from django.contrib import messages
        from django.db.models import Q
        from .models import Message
        
        original_message = Message.objects.get(message_id=message_id)
        
        # Mark original message as read when admin views it
        if not original_message.is_read:
            original_message.is_read = True
            original_message.save()
        
        # Get all messages between admin and this customer
        all_messages = Message.objects.filter(
            Q(sender=request.user, receiver=original_message.sender) |
            Q(sender=original_message.sender, receiver=request.user)
        ).order_by('created_at')
        
        if request.method == 'POST':
            reply_text = request.POST.get('reply_text')
            if reply_text:
                # Create reply message
                Message.objects.create(
                    sender=request.user,
                    receiver=original_message.sender,
                    message=reply_text,
                    is_read=False
                )
                messages.success(request, f'Reply sent to {original_message.sender.username}')
                # ========== CHANGED: Redirect to chat dashboard instead of message list ==========
                return HttpResponseRedirect(reverse('admin:chat_dashboard'))
                # ========== END CHANGE ==========
        
        context = {
            'original_message': original_message,
            'all_messages': all_messages,
            'title': f'Chat with {original_message.sender.username}',
        }
        return render(request, 'admin/chat_conversation.html', context)
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['chat_url'] = reverse('admin:chat_dashboard')
        return super().index(request, extra_context=extra_context)
    
    # ========== NEW: Override app index to redirect Messages app ==========
    def app_index(self, request, app_label, extra_context=None):
        """Redirect the Messages app index to chat dashboard"""
        if app_label == 'api' and 'message' in request.path.lower():
            return HttpResponseRedirect(reverse('admin:chat_dashboard'))
        return super().app_index(request, app_label, extra_context=extra_context)
    # ========== END NEW ==========
    
    # ========== NEW: Override get_app_list to change sidebar link ==========
    def get_app_list(self, request):
        """Modify the admin sidebar to point Messages link to chat dashboard"""
        app_list = super().get_app_list(request)
        
        for app in app_list:
            if app.get('app_label') == 'api':
                for model in app.get('models', []):
                    if model.get('object_name') == 'Message':
                        # Change the URL to point to chat dashboard
                        model['admin_url'] = reverse('admin:chat_dashboard')
                        model['add_url'] = reverse('admin:chat_dashboard')
        return app_list

admin.site.__class__ = CustomAdminSite

# Register all models with custom admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(Message, MessageAdmin)