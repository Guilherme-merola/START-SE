from django.db.models.manager import BaseManager
from django.http import HttpResponse
from django.shortcuts import render
from empresarios.models import Empresas

# Create your views here.
def sugestao(request) -> HttpResponse | None:
    if request.method == 'GET':
        return render(request, "sugestao.html", {"areas": Empresas.area_choices}) 
    
    elif request.method == 'POST':
        tipo = request.POST.get("tipo")
        areas = request.POST.getlist('area')
        valor = request.POST.get('valor')
        
        if tipo == "C": # Conservador
            empresas: BaseManager[Empresas] = Empresas.objects.filter(tempo_existencia='+5').filter(estagio='E')
        
        else:  # Despojado
            empresas: BaseManager[Empresas] = Empresas.objects.filter(tempo_existencia__in=['-6', "+6", "+1"]).exclude(estagio='E')

        empresas = empresas.filter(area__in=areas)
        
        empresas_selecionadas: list[Empresas] = [empresa for empresa in empresas if (float(valor) * 100 / float(empresa.valuation)) >= 1]
        print(empresas_selecionadas)
        return render(request, 'sugestao.html', {'empresas': empresas_selecionadas, 'areas': areas})
        