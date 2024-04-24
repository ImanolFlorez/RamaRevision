import Config
from Controller import Controller, ServerException, UnauthorizedException
from RamaClass import RamaProcessClass
from EvidenciaClass import EvidenciaClass
import datetime
from datetime import datetime
import traceback
import asyncio
import aiohttp
import base64
import urllib3
from requests import post, get
from Connection import Connection
import os
import sys
import threading
import ssl
import requests

def procesar_particion(particion,key,lock):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(principal(particion, key,lock))
    loop.close()

def printr(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


async def principal(listaProceso,Key,lock):
    try:
        try:
            Object_Database = Connection()
        except Exception as e:
            if not Object_Database.reconectar():
                raise Exception("No se pudo restablecer la conexión a la base de datos.")
        Object_Controller = Controller()
        rama = RamaProcessClass(Key)
        Evidencia = EvidenciaClass()
        for Cod23 in listaProceso:
            try:
                #printr(f"{Cod23} Consultando")
                data=rama.numero_radicacion(Cod23.replace("\n",""))
                if len(data['procesos'])>0:
                    lista = None
                    fecha_mas_reciente = None
                    for proceso in data['procesos']:
                        fecha_Ultima_Actuacion = proceso['fechaUltimaActuacion'] 
                        # Verificar si la fecha está en blanco
                        if fecha_Ultima_Actuacion is not None:
                            # Convertir la fecha a un formato manejable (puedes usar datetime.strptime si es necesario)
                            fecha_actual = datetime.strptime(str(proceso['fechaUltimaActuacion']), "%Y-%m-%dT%H:%M:%S")
                            # Si no tenemos fecha más reciente aún, o si la fecha actual es más reciente que la anterior, actualizamos
                            if fecha_mas_reciente is None or fecha_actual > fecha_mas_reciente:
                                lista = proceso
                                fecha_mas_reciente = fecha_actual
                    if lista is not None:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(Config.API_RAMAUNIFICADA + Config.GET_DOCX.format(id=lista['idProceso']), headers=rama.Set_Header(), proxy=Config.PROXIES) as respuesta:
                                if respuesta.status == 200:
                                    content_type = respuesta.headers.get('content-type')
                                    if 'application/json' in content_type:
                                        json_response = await respuesta.json()
                                        printr(f"{Cod23} Error al descargar el archivo DOCX. Código de estado: {respuesta.status}")
                                        Object_Controller.ActualizarProceso({
                                                "Procesos":[Cod23],
                                                "Machine":Key['Guid'],
                                                "Status":"2"
                                            },Object_Database)
                                        continue
                                    # Read the response data
                                    response_data = await respuesta.read()
                                    # Convert the response data to base64
                                    base64_data = base64.b64encode(response_data)
                                    Evidencia.InsertProceso((Cod23,datetime.now(),base64_data,datetime.now()),Object_Database.db)
                                    Object_Controller.ActualizarProceso({
                                                "Procesos":[Cod23],
                                                "Machine":Key['Guid'],
                                                "Status":"1"
                                            },Object_Database)
                                else:
                                    printr(f"{Cod23} Error al descargar el archivo DOCX")
                                    Object_Controller.ActualizarProceso({
                                                "Procesos":[Cod23],
                                                "Machine":Key['Guid'],
                                                "Status":"2"
                                            },Object_Database)
                                    #print("Failed to download the DOCX file. Status code:", response2.status_code)
                else:
                    printr(f"{Cod23} No Existe")
                    Object_Controller.ActualizarProceso({
                                        "Procesos":[Cod23],
                                        "Machine":Key['Guid'],
                                        "Status":"3"
                                    },Object_Database)
            except Exception as e:
                printr(f"{Cod23} Error: {e}")
                #printr(traceback.format_exc())
                Object_Controller.ActualizarProceso({
                                        "Procesos":[Cod23],
                                        "Machine":Key['Guid'],
                                        "Status":"2"
                                    },Object_Database)
    except Exception as e:
        printr(f"Error: {e}")
        printr(traceback.format_exc())
    

if __name__ == '__main__':
    try:
        arg1 = sys.argv[1]
    except Exception as e:
        arg1 = None
    Rama= RamaProcessClass()
    print('*** Inicio: '+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+"\n") 
    print("Version 1.6.4")   
    try:
        Connections = Connection()
        IsAuth,Key = Rama.authenticate(Connections)
        if(IsAuth):
            try:
                if arg1 is not None:
                    print(Rama.ConsultarProceso(arg1))
                else:
                    documentos=Rama.getBase(Key,Connections)
                    #documentos = None
                    if documentos is None:  
                        print('*** Sin Procesos....'+"\n")    
                    else:
                        print('*** Procesos....'+"\n")
                        num_procesos=int(Key['CPU'])
                        print('*** Cores: '+str(num_procesos)+"\n")
                        tamano_particion = len(documentos) // num_procesos
                        # Crea un bloqueo global
                        lock = threading.Lock()
                        # Crea una lista de hilos
                        hilos = []
                        # Divide los documentos en particiones y crea un hilo para cada partición
                        for i in range(num_procesos):
                            inicio = i * tamano_particion
                            fin = (i + 1) * tamano_particion if i != num_procesos - 1 else len(documentos)
                            particion = documentos[inicio:fin]
                            hilo = threading.Thread(target=procesar_particion, args=(particion, Key, lock))
                            hilos.append(hilo)
                            hilo.start()

                        # Espera a que todos los hilos terminen antes de continuar
                        for hilo in hilos:
                            hilo.join()
            except KeyboardInterrupt:
                print("\nSaliendo....")
            except Exception as e:
                print("\nError....\n")
                print(e)
                printr(traceback.format_exc())
        else:
            print("No Autorizado Solicite Permiso A Administrador.... \n")
    except KeyboardInterrupt:
        print("\nSaliendo....")
    except UnauthorizedException:
        print("\nExpulsado....")
    except ServerException as e:
        print("\nError server....\n")
        print(e)
        printr(traceback.format_exc())
    except Exception as e:
        print("\nError....\n")
        print(e)
        printr(traceback.format_exc())
    finally:
        Connections.close()
    print("*** Termino"+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+"\n")