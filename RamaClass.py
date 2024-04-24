import requests, socket
import json
import urllib3
import asyncio
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects
from os import path, name
import sys
import datetime
import traceback
import aiohttp
from Connection import Connection
import Config
import os
from Controller import Controller
import psutil
import getpass
import speedtest    

class RamaProcessClass:

    def __init__(self,Key=None):
        self.Key = Key
        self.url = Config.API_RAMAUNIFICADA
        self.proxies = {'https': Config.PROXIES}
        self.Object_Controller = Controller()

    def Set_Header(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'consultaprocesos.ramajudicial.gov.co:448',
            'Origin': Config.ORIGIN,
            'Referer': Config.ORIGIN,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Chromium";v="118", " Not A;Brand";v="99", "Google Chrome";v="118"',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            'Sec-Ch-Ua-Platform': '"Linux"'
            }
        return headers

    def numero_radicacion(self, numero,soloactivos=False,pagina=1):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        Consulta = Config.PROCESOS.format(numero=numero,soloactivos=soloactivos,pagina=pagina)
        r = requests.get(self.url+Consulta, verify=False, headers=self.Set_Header(),proxies=self.proxies)
        #print(r.json())
        return r.json()

    def authenticate(self,Connections):
        result = False,None
        try:
            fileAuth = path.join(path.expanduser('~'), '.authRamaRevision')
            print(fileAuth)
            ControllerObject = Controller()
            try:
                if(path.exists(fileAuth) == False):
                    self.__Host = {
                        'Hostname': socket.gethostname(),
                        'IP': socket.gethostbyname(socket.gethostname()),
                        'SO': ('windows' if name == 'nt' else 'unix'),
                        'IPV4': requests.get('https://api.ipify.org/', timeout=5).text,
                        'IPV6': requests.get('https://api64.ipify.org/', timeout=5).text
                    }
                    self.__Host['RAM']=psutil.virtual_memory().total / (1024 ** 3)
                    self.__Host['USUARIO']=getpass.getuser()
                    test=speedtest.Speedtest()
                    self.__Host['DESCARGA']=test.download() / (1024 ** 2)
                    self.__Host['SUBIDA']=test.upload() / (1024 ** 2)
                    self.__Host['CPU']=os.cpu_count()
                    self.__Host['UBICACION']=os.getcwd()
                    self.__Host['BASE']="Diaria"
            except (Timeout, ConnectionError, TooManyRedirects):
                print('Error consultando informacion de red.')
            else:
                try:
                    if(path.exists(fileAuth) == False):
                        nombre = input('Ingrese su nombre: ').strip()

                        if(nombre != '' and len(nombre) >= 4):
                            DatosRegistrar = self.__Host
                            DatosRegistrar["Name"] = nombre
                            with open(fileAuth, 'w') as file:
                                file.write(ControllerObject.Registrar_Agente(DatosRegistrar))
                        else:
                            print("Nombre invalido.")

                    with open(fileAuth) as file:
                        key = file.readline()
                        
                except PermissionError:
                    print("Permiso denegado para generar key.")
                except FileNotFoundError:
                    print("Permiso denegado para consultar key.")
                else:
                    Agente = ControllerObject.consultar_agente(key,Connections)
                    if(Agente != None):
                        if Agente['Status']=='0':
                            result = True,Agente
                        else:
                            result = False,Agente
                    else:
                        print("Error de autenticación.")
            return result
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return False,None

    def getBase(self,key,Connections):
        try:
            Connections.db.ping()
        except Exception as e:
            if not Connections.reconectar():
                # Manejo del fallo en la reconexión
                # Aquí puedes decidir qué hacer si no se logra reconectar
                # Por ejemplo, detener la ejecución, levantar una alerta, etc.
                raise Exception("No se pudo restablecer la conexión a la base de datos.")
        try:
            ControllerObject = Controller()
            return ControllerObject.GetBase(key,Connections)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return None