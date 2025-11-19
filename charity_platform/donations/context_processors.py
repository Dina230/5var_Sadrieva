from django.db.models import Sum
from .models import Donation

def total_donations(request):
    """Контекстный процессор для добавления общей суммы пожертвований во все шаблоны"""
    total = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    return {
        'total_donations': total,
    }