from email.policy import HTTP
from django.db.models.manager import BaseManager
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from empresarios.models import Documento, Empresas
from .models import PropostaInvestimento
from django.contrib.messages import constants
from django.contrib import messages


# Create your views here.
def sugestao(request) -> HttpResponse | None:
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
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


def ver_empresa(request, id) -> HttpResponse:
    empresa: Empresas = Empresas.objects.get(id=id)
    documentos: BaseManager[Documento] = Documento.objects.filter(empresa=empresa)
    propostas: BaseManager[PropostaInvestimento] = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    percentual_vendido: float = float(sum(x.percentual for x in propostas))
    limiar: float = empresa.percentual_equity * 0.8
    concretizado: bool = True if percentual_vendido >= limiar else False
    percentual_disponivel = empresa.percentual_equity - percentual_vendido
    
    return render(request, 'ver_empresa.html', {
        "empresa": empresa, 
        "documentos": documentos,
        "percentual_vendido": int(percentual_vendido),
        "concretizado": concretizado,
        "percentual_disponivel": percentual_disponivel,
    })


def realizar_proposta(request, id) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa: Empresas = Empresas.objects.get(id=id)
    
    propostas_aceitas: BaseManager[PropostaInvestimento] = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    total_aceito: float = sum(x.percentual for x in propostas_aceitas)
    
    if total_aceito + float(percentual) > empresa.percentual_equity:
        messages.add_message(request, constants.WARNING, "O percentual solicitado ultrapassa o percentual máximo.")
        return redirect(f"/investidores/ver_empresa/{id}")

    valuation: float = (100 * int(valor) / int(percentual))
    
    if valuation < float(empresa.valuation) / 2:
        messages.add_message(request, constants.WARNING, f"Seu valuation proposto foi R$:{valuation :.2f} e deve ser no minimo R$:{(float(empresa.valuation)/2) :.2f}")
        return redirect(f"/investidores/ver_empresa/{id}")
    
    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user,
    )
    
    pi.save()
    return redirect(f'/investidores/assinar_contrato/{pi.id}')


def assinar_contrato(request, id):
    pi: PropostaInvestimento = PropostaInvestimento.objects.get(id=id)
    
    if pi.status != "AS":
        raise Http404()
    
    if request.method == "GET":
        return render(request, "assinar_contrato.html", {
            "pi": pi,
        })
        
    elif request.method == "POST":
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        
        pi.selfie = selfie
        pi.rg = rg       
        pi.status = 'PE'

        pi.save()
        
        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')
        