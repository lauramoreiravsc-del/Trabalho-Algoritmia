import requests
from geopy.geocoders import Nominatim

RESTAURANTE_ENDERECO = "Universidade do Minho - Campus de Azurém"
RESTAURANTE_COORDS = None 
RAIO_MAXIMO_ENTREGA = 30 


def obter_coordenadas(endereco):
    """
    Converte um endereço em coordenadas (latitude, longitude)
    Usa OpenStreetMap/Nominatim (gratuito, sem chave API)
    """
    try:
        geolocator = Nominatim(user_agent="send2you")
        location = geolocator.geocode(endereco, timeout=10)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception:
        return None


def inicializar_restaurante():
    """
    Obtém as coordenadas do restaurante na primeira execução
    """
    global RESTAURANTE_COORDS
    
    if RESTAURANTE_COORDS is None:
        
        coords = obter_coordenadas(RESTAURANTE_ENDERECO)
        
       
    
        if coords:
            RESTAURANTE_COORDS = coords
            return True
        else:
            return False
    return True


def calcular_rota(coords_origem, coords_destino):
    """
    Calcula a rota entre dois pontos usando OSRM (Open Source Routing Machine)
    Retorna: (distancia_km, tempo_minutos)
    """
    try:
        origem_str = f"{coords_origem[1]},{coords_origem[0]}"
        destino_str = f"{coords_destino[1]},{coords_destino[0]}"
        
        url = f"http://router.project-osrm.org/route/v1/driving/{origem_str};{destino_str}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("routes"):
                route = data["routes"][0]
                
                distancia_km = route["distance"] / 1000
                
                tempo_minutos = route["duration"] / 60
                
                return (distancia_km, tempo_minutos)
        
        return None
        
    except Exception:
        return None

def calcular_entrega(endereco_cliente):
    """
    Calcula a distância e tempo de entrega do restaurante para o cliente
    
    Retorna:
        tupla: (distancia_km, tempo_minutos) ou None se houver erro
    """
    if not inicializar_restaurante():
        return None
    
    coords_cliente = obter_coordenadas(endereco_cliente)
    
    if not coords_cliente:
        return None
    
    resultado = calcular_rota(RESTAURANTE_COORDS, coords_cliente)
    
    if resultado:
        distancia, tempo = resultado
        return (distancia, tempo)
    
    return None


def verificar_raio_entrega(distancia_km):
    """
    Verifica se a entrega está dentro do raio máximo permitido
    Retorna: (permitido: bool, mensagem: str)
    """
    if distancia_km > RAIO_MAXIMO_ENTREGA:
        return False, f" Desculpe, o endereço fica a {distancia_km:.2f} km do restaurante. O raio máximo de entrega é {RAIO_MAXIMO_ENTREGA} km."
    return True, " Endereço dentro do raio de entrega."


def exibir_info_entrega(endereco_cliente, distancia_km, tempo_minutos):
    """
    Exibe informações formatadas sobre a entrega
    """
    print("\n" + "="*50)
    print(" INFORMAÇÕES DE ENTREGA")
    print("="*50)
    print(f" Endereço cliente: {endereco_cliente}")
    print(f" Distância: {distancia_km:.2f} km")
    print(f" Tempo estimado: {tempo_minutos:.0f} minutos")
    print("="*50 + "\n")
