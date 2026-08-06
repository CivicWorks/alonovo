from django.shortcuts import render
from django.contrib import admin as django_admin


def data_guide_view(request):
    """Admin data entry guide at /admin/data-guide/"""
    context = django_admin.site.each_context(request)
    context['title'] = 'Data Guide'
    return render(request, 'admin/data_guide.html', context)
