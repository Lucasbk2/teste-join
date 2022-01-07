from branca.element import MacroElement
from django.shortcuts import render, redirect
from django.views import View
from folium.utilities import validate_location
import decimal
from decimal import *
from .models import Ponto
import folium
import datetime
from jinja2.environment import Template


# Override no marcador para fazer funcão do clique abrir modal
class MarkerClick(folium.Marker):
    def __init__(self, location=None, popup=None, tooltip=None, icon=None,
                 draggable=False, id=None, **kwargs):
        super(MarkerClick, self).__init__()
        self._name = 'Marker'
        self.location = validate_location(location) if location else None
        if icon is not None:
            self.add_child(icon)
            self.icon = icon
        self.id = id

    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{ this.get_name() }} = L.marker(
                    {{ this.location|tojson }},
                    {{ this.options|tojson }}
                ).addTo({{ this._parent.get_name() }});
                {{this.get_name()}}.on('click',function executar(){location.replace("/{{this.id}}");})
            {% endmacro %}
            """)


# Gera todos os pontos cadastrados no mapa
# Pontos com data expirada comparada a hoje ficam vermelhas no mapa
def gera_pontos(mapa, id_pontos):
    pontos = Ponto.objects.all()

    for ponto in pontos:
        if ponto.data_expiracao < datetime.datetime.today().date():
            marker = MarkerClick(
                [float(ponto.latitude), float(ponto.longitude)], id=ponto.id, icon=folium.Icon(color='red'))
        else:
            marker = MarkerClick(
                [float(ponto.latitude), float(ponto.longitude)], id=ponto.id, icon=folium.Icon(color='blue'))
        id_pontos.append(marker._id)
        marker.add_to(mapa)
    return mapa, id_pontos


# Realiza formatação de data para input do bootstrap
def formata_data(data):
    if data.day < 10:
        dia = "0" + str(data.day)
    else:
        dia = str(data.day)
    if data.month < 10:
        mes = "0" + str(data.month)
    else:
        mes = str(data.month)

    ano = str(data.year)

    return dia, mes, ano


class HomePage(View):
    def get(self, request, id=None):
        dia, mes, ano = '', '', ''
        ponto_localizado = None
        if not id:  # caso nenhum pondo foi selecionado, renderiza inicio
            mapa = folium.Map(location=[-14.2296, -50.1855], zoom_start=5)
        else:  # abre ponto caso selecionado
            ponto_localizado = Ponto.objects.get(id=id)
            mapa = folium.Map(location=[ponto_localizado.latitude, ponto_localizado.longitude], zoom_start=8)
            # formata data para input
            dia, mes, ano = formata_data(ponto_localizado.data_expiracao)

        # Preenche pontos no mapa
        id_pontos = []
        mapa, id_pontos = gera_pontos(mapa, id_pontos)

        # Permite o usuário clicar em um ponto aleatorio da tela para facilitar pegar a latitude/longitude
        mapa.add_child(folium.LatLngPopup())

        # renderização do mapa + tela
        mapa = mapa.get_root().render()
        context = {'mapa': mapa, 'pontos': id_pontos, 'ponto_localizado': ponto_localizado, 'dia': dia, 'mes': mes,
                   'ano': ano}
        return render(request, 'mainapp/home.html', context)

    def post(self, request, id=None):

        # Define metodo a ser realizado
        for x in request.POST:
            if x == 'salvar':
                metodo = x
            if x == 'atualizar':
                metodo = x
            elif x == 'deletar':
                metodo = x

        erro = None
        ponto_localizado = None
        dia, mes, ano = '', '', ''
        # salva, deleta ou cria um ponto dependendo do método selecionado
        if metodo == 'salvar':
            try:  # usado para validar se a latitude ou longitude estiverem incorretas
                Ponto.objects.create(
                    nome=request.POST['nome'], latitude=Decimal(request.POST['latitude'].replace(',', '.')),
                    longitude=Decimal(request.POST['longitude'].replace(',', '.')), data_expiracao=request.POST['data']
                )
                ponto_localizado = Ponto.objects.last()
                dia, mes, ano = formata_data(ponto_localizado.data_expiracao)
                mapa = folium.Map(location=[request.POST['latitude'].replace(',', '.'),
                                            Decimal(request.POST['longitude'].replace(',', '.'))], zoom_start=5)
            except:
                erro = 'Erro encontrado, tente novamente com os dados dos campos corretamente'
                mapa = folium.Map(location=[-14.2296, -50.1855], zoom_start=5)

        elif metodo == 'atualizar':
            ponto = Ponto.objects.filter(id=id)
            try:  # usado para validar se a latitude ou longitude estiverem incorretas
                ponto.update(
                    nome=request.POST['nome'], latitude=Decimal(request.POST['latitude'].replace(',', '.')),
                    longitude=Decimal(request.POST['longitude'].replace(',', '.')), data_expiracao=request.POST['data']
                )
                ponto.first().save()
            except:
                erro = 'Erro encontrado, tente novamente com os dados dos campos corretamente'
            ponto_localizado = ponto.first()
            dia, mes, ano = formata_data(ponto_localizado.data_expiracao)
            mapa = folium.Map(location=[ponto.first().latitude, ponto.first().longitude], zoom_start=5)

        elif metodo == 'deletar':
            ponto = Ponto.objects.filter(id=id)
            mapa = folium.Map(location=[ponto.first().latitude, ponto.first().longitude], zoom_start=5)
            ponto.delete()

        # Preenche pontos no mapa
        id_pontos = []
        mapa, id_pontos = gera_pontos(mapa, id_pontos)

        # Permite o usuário clicar em um ponto aleatorio da tela para facilitar pegar a latitude/longitude
        mapa.add_child(folium.LatLngPopup())

        # renderização do mapa + tela
        mapa = mapa.get_root().render()
        context = {'mapa': mapa, 'pontos': id_pontos, 'erro': erro, 'ponto_localizado': ponto_localizado, 'dia': dia,
                   'mes': mes, 'ano': ano}
        return render(request, 'mainapp/home.html', context)
