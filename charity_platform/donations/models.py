from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class CharityProject(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершенный'),
        ('pending', 'На рассмотрении'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание')
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Целевая сумма',
        default=0
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Собранная сумма'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    deadline = models.DateTimeField(verbose_name='Срок сбора')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус'
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на изображение',
        help_text='URL изображения проекта (опционально)'
    )

    class Meta:
        verbose_name = 'Благотворительный проект'
        verbose_name_plural = 'Благотворительные проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        """Процент выполнения цели сбора"""
        try:
            if self.target_amount and float(self.target_amount) > 0:
                percentage = (float(self.current_amount) / float(self.target_amount)) * 100
                return min(100, round(percentage, 1))
            return 0
        except (TypeError, ValueError):
            return 0

    @property
    def days_remaining(self):
        """Количество оставшихся дней"""
        try:
            if self.deadline:
                now = timezone.now()
                remaining = self.deadline - now
                return max(0, remaining.days)
            return 0
        except (TypeError, ValueError):
            return 0

    @property
    def is_active(self):
        """Активен ли проект для пожертвований"""
        try:
            return (
                    self.status == 'active' and
                    self.days_remaining > 0 and
                    float(self.current_amount) < float(self.target_amount)
            )
        except (TypeError, ValueError):
            return False

    def save(self, *args, **kwargs):
        """Переопределяем save для валидации"""
        # Убеждаемся, что суммы не None
        if self.target_amount is None:
            self.target_amount = 0
        if self.current_amount is None:
            self.current_amount = 0

        # Убеждаемся, что текущая сумма не превышает целевую
        if float(self.current_amount) > float(self.target_amount):
            self.current_amount = self.target_amount

        # Автоматически меняем статус если собрана целевая сумма
        if float(self.current_amount) >= float(self.target_amount) and self.status == 'active':
            self.status = 'completed'

        super().save(*args, **kwargs)


class Donation(models.Model):
    project = models.ForeignKey(
        CharityProject,
        on_delete=models.CASCADE,
        related_name='donations',
        verbose_name='Проект'
    )
    donor_name = models.CharField(max_length=100, verbose_name='Имя жертвователя')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        verbose_name='Сумма пожертвования'
    )
    email = models.EmailField(verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата пожертвования')
    is_anonymous = models.BooleanField(default=False, verbose_name='Анонимно')

    class Meta:
        verbose_name = 'Пожертвование'
        verbose_name_plural = 'Пожертвования'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.donor_name} - {self.amount} руб.'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Обновляем текущую сумму проекта
        if is_new:
            total = Donation.objects.filter(
                project=self.project
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0
            self.project.current_amount = total
            self.project.save()