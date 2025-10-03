from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Petition, Vote


@login_required
def petition_list(request):
    petitions = Petition.objects.all().order_by('-created_at')
    return render(request, 'petitions/petition_list.html', {'petitions': petitions})


@login_required
def petition_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        Petition.objects.create(
            title=title,
            description=description,
            created_by=request.user,
            created_at=timezone.now()
        )
        return redirect('petition_list')
    return render(request, 'petitions/petition_create.html')


@login_required
def petition_detail(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    if request.method == "POST":
        # record a vote if user hasn’t already
        Vote.objects.get_or_create(petition=petition, user=request.user)
        return redirect('petition_detail', pk=petition.pk)
    return render(request, 'petitions/petition_detail.html', {'petition': petition})
