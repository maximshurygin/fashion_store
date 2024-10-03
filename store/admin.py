from django.contrib import admin

from store.models import Size, Brand, Category, Product, ProductInventory, ProductImage, Color, Order


# Register your models here.

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    exclude = ('sku', 'slug')
    inlines = [ProductImageInline]


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    exclude = ('sku', 'created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price', 'status')


admin.site.register(ProductImage)

admin.site.register(Color)
