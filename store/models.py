import uuid
import random
import time

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unidecode import unidecode
from django.utils.text import slugify

from django.db import models
from django.urls import reverse


# Create your models here.

def custom_slugify(value):
    return slugify(unidecode(value))


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='название')
    slug = AutoSlugField(populate_from='name', slugify=custom_slugify)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list') + f'?category={self.slug}'

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Size(models.Model):
    name = models.CharField(max_length=15, unique=True, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'размер'
        verbose_name_plural = 'размеры'


class Color(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'цвет'
        verbose_name_plural = 'цвета'


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images', verbose_name='товар')
    image = models.ImageField(upload_to='product_images', verbose_name='фотография')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name='альтернативный текст')

    def __str__(self):
        return f'{self.product.name} - {self.image.name}'

    class Meta:
        verbose_name = 'фотография'
        verbose_name_plural = 'фотографии'


class Product(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('U', 'Универсальный'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')
    description = models.TextField(verbose_name='описание')
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, verbose_name='фирма')
    sizes = models.ManyToManyField('Size', related_name='products', verbose_name='размеры')
    colors = models.ManyToManyField('Color', related_name='products', verbose_name='цвета')
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE,
                                 verbose_name='категория')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='пол')
    sku = models.CharField(max_length=20, blank=True, null=True, verbose_name='артикул')
    slug = AutoSlugField(populate_from='name', slugify=custom_slugify)

    def save(self, *args, **kwargs):
        if not self.sku:
            timestamp_part = str(int(time.time()))[-5:]
            random_part = str(random.randint(100, 999))
            self.sku = f'{timestamp_part}{random_part}'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        colors_list = ', '.join([color.name for color in self.colors.all()])
        return f'{self.name} - {self.brand.name} - {self.get_gender_display()} - {colors_list}'

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['brand']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
        ]


class ProductInventory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='товар')
    size = models.ForeignKey('Size', on_delete=models.CASCADE, verbose_name='размер')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, verbose_name='цвет')
    stock = models.PositiveIntegerField(default=0, verbose_name='количество на складе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата обновления')

    def __str__(self):
        return f'{self.product.name} - {self.size} - {self.color} - {self.stock} шт.'

    class Meta:
        verbose_name = 'учет товара'
        verbose_name_plural = 'учет товаров'
        unique_together = ('product', 'size', 'color')
        indexes = [
            models.Index(fields=['product', 'size', 'color']),
        ]


class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина пользователя: {self.user.email if self.user else "Аноним"}'

    @property
    def total_price(self):
        # Используем select_related для подгрузки связанных данных
        return sum(
            item.product_inventory.product.price * item.quantity
            for item in self.items.select_related('product_inventory__product')
        )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items', verbose_name='корзина')
    product_inventory = models.ForeignKey('ProductInventory', on_delete=models.CASCADE, verbose_name='товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='количество')

    def __str__(self):
        return f'{self.product_inventory.product.name} ({self.product_inventory.size.name}, {self.product_inventory.color.name}) - {self.quantity} шт.'

    def get_total_price(self):
        return self.product_inventory.product.price * self.quantity

    class Meta:
        verbose_name = 'предмет корзины'
        verbose_name_plural = 'предметы корзины'


class FavouriteItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='favorites',
                             verbose_name='пользователь')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorites', verbose_name='товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата добавления')

    def __str__(self):
        return f'{self.user} - {self.product}'

    class Meta:
        verbose_name = 'избранный товар'
        verbose_name_plural = 'избранные товары'
        unique_together = ('user', 'product')


class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'В обработке'),
        ('C', 'Завершен'),
        ('F', 'Отменен'),
        ('S', 'Отправлен'),
        ('D', 'Доставлен'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders',
                             verbose_name='пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата заказа')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='общая стоимость')
    delivery_address = models.TextField(verbose_name='адрес доставки')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', verbose_name='статус')

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от {self.user.email}'

    def get_absolute_url(self):
        return reverse('store:order_detail', kwargs={'order_id': self.id})

    def cancel_order(self):
        if self.status not in ['C', 'F']:
            for item in self.items.all():
                item.product_inventory.stock += item.quantity
                item.product_inventory.save()
            self.status = 'F'
            self.save()

    def calculate_total_price(self):
        total = sum(
            item.product_inventory.product.price * item.quantity for item in self.items.all()
        )
        self.total_price = total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_total_price()
        Order.objects.filter(pk=self.pk).update(total_price=self.total_price)


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items', verbose_name='заказ')
    product_inventory = models.ForeignKey('ProductInventory', on_delete=models.CASCADE, verbose_name='товар')
    quantity = models.PositiveIntegerField(verbose_name='количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена за единицу')

    def get_total_price(self):
        return self.price * self.quantity

    def clean(self):
        if self.quantity > self.product_inventory.stock:
            raise ValidationError(f'Недостаточно товара {self.product_inventory.product.name} на складе.')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:
            self.product_inventory.stock -= self.quantity
            self.product_inventory.save()
            self.price = self.product_inventory.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product_inventory.product.name} - {self.quantity} шт.'

    class Meta:
        verbose_name = 'заказанный товар'
        verbose_name_plural = 'заказанные товары'
