import Config
import json
from requests import post, get
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects
import urllib3
import traceback
from Connection import Connection


class Controller:
    def __init__(self):
        self.__Headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-type": "application/json",
        "EXTRACT-VERSION": "2.0"
    }

    def ConsultarProceso(self,Proceso):
        urlConsulta = str(Config.API_LUPA) + str(Config.SEARCH_PROCESO).format(proceso=Proceso)
        result = self.__excecute__(urlConsulta)
        return result

    def ActualizarProceso(self,data,Connections):
        Result=Connections.Actualizar_Proceso(data)
        return Result
    
    def Registrar_Agente(self,Agente):
        id_insert = ''
        urlConsulta = str(Config.API_LUPA) + str(Config.REGISTRO_AGENTE)
        print(urlConsulta)
        result = self.__excecute__(urlConsulta, "POST", json.dumps(Agente))
        if (result["Status"] and "Data" in result):
            id_insert = result["Data"]

        return str(id_insert)

    def consultar_agente(self,key,Connections):
        Result=Connections.Select_Agente(key)
        return Result
    
    def GetBase(self,data,Connections):
        Result=Connections.Select_Base(Id=data['Guid'],CPU=data['CPU'],Base=data['Base'],Tipo=int(data['Tipo']))
        return Result

    def setAgentId(self, agentId):
        self.__Headers["AUTHORIZATION-USER"] = str(agentId)

    def __excecute__(self,urlConsulta, method="GET", datos={}):
        Rst = {"Status": False, "Data": {}}
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            if method == "POST":
                response = post(urlConsulta,
                                #verify=False,
                                headers=self.__Headers,
                                timeout=60,
                                data=datos)
            elif method == "GET":
                response = get(urlConsulta,
                               #verify=False,
                               headers=self.__Headers,
                               timeout=60)
            else:
                response = get(urlConsulta,
                               #verify=False,
                               headers=self.__Headers,
                               timeout=60)

            Rst["status_code"] = response.status_code

            if response.status_code == 200:
                Rst = response.json()
            else:
                Rst = response.json()
            return Rst
        except Exception as e:
            return Rst
    
class UnauthorizedException(Exception):

    def __init__(self, message):
        super().__init__(message)

class ServerException(Exception):

    def __init__(self, message):
        super().__init__(message)