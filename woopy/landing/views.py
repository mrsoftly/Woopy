from django.shortcuts import render
from app.models import Plan

# Create your views here.
def home(request):
    
    return render(request,'home.html')

def prices(request):
    plans = Plan.objects.all()
    return render(request,'prices.html', {'plans': plans})
def contact(request):
    return render(request,'form.html')