from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Проверка, существует ли пользователь с данным email
        if not User.objects.filter(email='admin@mail.ru').exists():
            user = User.objects.create(
                email='admin@mail.ru',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )

            # Установка пароля
            user.set_password('ggwp12345')
            user.save()

            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))