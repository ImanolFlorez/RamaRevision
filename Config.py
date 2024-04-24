import requests

r=requests.get("http://181.79.32.58:5000/api/config")
data=r.json()
# Almacenar variables de entorno en variables globales
PROXIES= data['PROXIES']
API_LUPA= data['API_LUPA']
REGISTRO_AGENTE= data['REGISTRO_AGENTE_EVIDENCIA']
BUSCAR_AGENTE= data['BUSCAR_AGENTE_EVIDENCIA']
IP_SERVER=data['IP_SERVER']
PORT_SERVER= data['PORT_SERVER']
USER_SERVER= data['USER_SERVER']
PASS_SERVER= data['PASS_SERVER']
DATABASE_SERVER= data['DATABASE_SERVER_EVIDENCIA']
API_RAMAUNIFICADA= data['API_RAMAUNIFICADA']
GET_DOCX= data['GET_DOCX']
PROCESOS = data['PROCESOS']
ORIGIN = data['ORIGIN']
