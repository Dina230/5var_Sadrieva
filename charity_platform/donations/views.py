from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count
from django.contrib import messages
from django.utils import timezone
from .models import CharityProject, Donation
from .forms import DonationForm


def index(request):
    """Главная страница"""
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_projects = CharityProject.objects.count()

    # Правильный расчет активных проектов
    active_projects = CharityProject.objects.filter(status='active').count()

    # Альтернативный расчет: проекты которые действительно активны (по логике is_active)
    actually_active_projects = 0
    for project in CharityProject.objects.filter(status='active'):
        if project.is_active:
            actually_active_projects += 1

    recent_donations = Donation.objects.select_related('project').order_by('-created_at')[:5]

    # Показываем действительно активные проекты на главной
    featured_projects = []
    for project in CharityProject.objects.filter(status='active')[:6]:
        if project.is_active:
            featured_projects.append(project)
        if len(featured_projects) >= 3:
            break

    context = {
        'total_donations': total_donations,
        'total_projects': total_projects,
        'active_projects': active_projects,  # Просто по статусу
        'actually_active_projects': actually_active_projects,  # По реальной активности
        'recent_donations': recent_donations,
        'featured_projects': featured_projects,
    }
    return render(request, 'donations/index.html', context)


def projects_list(request):
    """Список всех проектов"""
    projects = CharityProject.objects.all().order_by('-created_at')
    return render(request, 'donations/projects.html', {'projects': projects})


def project_detail(request, project_id):
    """Детальная страница проекта"""
    project = get_object_or_404(CharityProject, id=project_id)
    donations = project.donations.all().order_by('-created_at')[:10]

    context = {
        'project': project,
        'donations': donations,
    }
    return render(request, 'donations/project_detail.html', context)


def donation_form(request, project_id):
    """Форма для пожертвования"""
    project = get_object_or_404(CharityProject, id=project_id)

    if not project.is_active:
        messages.warning(request, 'Этот проект больше не принимает пожертвования.')
        return redirect('project_detail', project_id=project_id)

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.project = project
            donation.save()

            messages.success(
                request,
                f'Спасибо за ваше пожертвование в размере {donation.amount} руб.!'
            )
            return redirect('project_detail', project_id=project_id)
    else:
        form = DonationForm()

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'donations/donation_form.html', context)


def statistics(request):
    """Страница статистики"""
    # Общая статистика
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_donors = Donation.objects.values('email').distinct().count()
    donation_count = Donation.objects.count()
    avg_donation = total_donations / donation_count if donation_count > 0 else 0

    # Статистика по проектам
    projects_stats = CharityProject.objects.annotate(
        donation_count=Count('donations'),
        total_donated=Sum('donations__amount')
    ).order_by('-current_amount')

    # Ежемесячная статистика (исправленная версия для SQLite)
    monthly_stats = []
    donations_by_month = Donation.objects.extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')

    for stat in donations_by_month:
        monthly_stats.append({
            'month': stat['month'],
            'total': float(stat['total'] or 0),
            'count': stat['count']
        })

    # Статистика по дням (последние 30 дней)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_donations = Donation.objects.filter(created_at__gte=thirty_days_ago)
    recent_total = recent_donations.aggregate(total=Sum('amount'))['total'] or 0
    recent_count = recent_donations.count()

    # Топ жертвователей с расчетом среднего чека
    top_donors_data = Donation.objects.values('donor_name', 'email').annotate(
        total_donated=Sum('amount'),
        donation_count=Count('id')
    ).order_by('-total_donated')[:10]

    # Рассчитываем средний чек для каждого жертвователя
    top_donors = []
    for donor in top_donors_data:
        avg_check = donor['total_donated'] / donor['donation_count'] if donor['donation_count'] > 0 else 0
        top_donors.append({
            'donor_name': donor['donor_name'],
            'email': donor['email'],
            'total_donated': donor['total_donated'],
            'donation_count': donor['donation_count'],
            'avg_check': round(avg_check, 2)
        })

    context = {
        'total_donations': total_donations,
        'total_donors': total_donors,
        'avg_donation': round(avg_donation, 2),
        'projects_stats': projects_stats,
        'monthly_stats': monthly_stats,
        'recent_total': recent_total,
        'recent_count': recent_count,
        'top_donors': top_donors,
    }
    return render(request, 'donations/statistics.html', context)