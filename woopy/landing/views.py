from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'home.html')

def prices(request):
    return render(request,'prices.html')
def contact(request):
    return render(request,'form.html')