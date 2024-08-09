from email import message
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, UserManager
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth

# Create your views here.
def cadastro(request) -> HttpResponse:
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, "As senhas não coincidem.")
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, "A senha precisa possuir pelo menos 6 digitos.")
            return redirect('/usuarios/cadastro')
        
        users: UserManager[User] = User.objects.filter(username=username)
        
        if users.exists():
            messages.add_message(request, constants.ERROR, "Ja existe um usuário com este username.")
            return redirect('/usuarios/cadastro')
        else:
            user: User = User.objects.create_user(username=username, password=senha)
     
        return redirect('/usuarios/logar')
    
def logar(request) -> HttpResponse:
    if request.method == "GET":
        return render(request, "logar.html")
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user: auth.AbstractUser | None = auth.authenticate(request, username=username, password=senha)
        
        if user:
            auth.login(request, user)
            return redirect('/empresarios/cadastrar_empresa')
        else:
            messages.add_message(request, constants.ERROR, "Login ou senha inválidos.")
            return render(request, "logar.html")
    