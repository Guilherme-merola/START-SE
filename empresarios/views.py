from math import log
from django.db.models.manager import BaseManager
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render

import empresarios
from .models import Empresas
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.
def cadastrar_empresa(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse | None:
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', 
                      {'tempo_existencia': Empresas.tempo_existencia_choices, 
                       'areas': Empresas.area_choices })
        
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')
        
        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()
            
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/empresarios/cadastrar_empresa')
        
        messages.add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')
            
            
def listar_empresas(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        empresas: BaseManager[Empresas] = Empresas.objects.filter(user=request.user)
        #Fazer um filtro das empresas
        return render(request, "listar_empresas.html", {"empresas": empresas})
    

def empresa(request, id):
    empresa: Empresas = Empresas.objects.get(id=id)
    
    if request.method == "GET":
        return render(request, "empresa.html", {"empresa": empresa})
