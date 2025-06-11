from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet


from .models import *
# Register your models here.




class ProductVariantInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(not form.cleaned_data.get('DELETE', False) and form.cleaned_data for form in self.forms):
            raise ValidationError("Iltimos, kamida bitta variant qo‘shing.")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    formset = ProductVariantInlineFormSet
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'price_usd', 'discount',
                    'category', 'quantity', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total_price')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price','size')
    list_filter = ('order', 'product')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(BigPic)
admin.site.register(Favorite)
admin.site.register(Size)