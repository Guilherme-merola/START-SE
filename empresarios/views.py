from django.db.models.manager import BaseManager
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render

from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.
def cadastrar_empresa(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse | None:
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', 
                      {'tempo_existencia': Empresas.tempo_existencia_choices, 
                       'areas': Empresas.area_choices,})
        
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
    

def empresa(request, id) -> HttpResponse | None:
    empresa: Empresas = Empresas.objects.get(id=id)
    
    if request.method == "GET":
        propostas_investimentos: BaseManager[PropostaInvestimento] = PropostaInvestimento.objects.filter(empresa=empresa)
        propostas_investimentos_enviadas: BaseManager[PropostaInvestimento] = propostas_investimentos.filter(status="PE")
        percentual_vendido: float = sum(x.percentual for x in propostas_investimentos if x.status == "PA")
        total_captado: float = float(sum(x.valor for x in propostas_investimentos if x.status == "PA"))
        valuation_atual: float = 100 * total_captado / percentual_vendido if percentual_vendido != 0 else 0

        documentos: BaseManager[Documento] = Documento.objects.filter(empresa=empresa) 
        
        return render(request, "empresa.html", {
            "empresa": empresa,
            "documentos": documentos,
            "propostas_investimento_enviadas": propostas_investimentos_enviadas,
            "percentual_vendido": int(percentual_vendido),
            "total_captado": total_captado,
            "valuation_atual": valuation_atual,
        })
    
    
def add_doc(request, id) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Está empresa não é sua.")
        return redirect(f'/empresarios/listar_empresas')
    
    if not '.pdf' in arquivo.name:
        messages.add_message(request, constants.ERROR, "Apenas PDF's são aceitos.")
        return redirect(f'/empresarios/empresa/{id}')

    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{id}')
    
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo,
    )

    documento.save()
    
    messages.add_message(request, constants.SUCCESS, "Cadastrado com Sucesso.")
    return redirect(f'/empresarios/empresa/{id}')

    
def excluir_doc(request, id) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    documento: Documento = Documento.objects.get(id=id)
    
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Está empresa não é sua.")
        return redirect(f'/empresarios/listar_empresas')
     
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluido com sucesso")
    return redirect(f"/empresarios/empresa/{documento.empresa.id}")


def add_metrica(request, id) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get("titulo")
    valor = request.POST.get("valor")
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor,
    )
    
    metrica.save()
    messages.add_message(request, constants.SUCCESS, "Métrica adicionada com sucesso.")
    return redirect(f"/empresarios/empresa/{empresa.id}")


def gerenciar_proposta(request, id) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    acao = request.GET.get('acao')
    pi: PropostaInvestimento = PropostaInvestimento.objects.get(id=id)
    
    if acao == "aceitar":
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita.')
        pi.status = 'PA'
        
    else:
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada.')
        pi.status = 'PR'
    
    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')
