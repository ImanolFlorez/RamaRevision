from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
import pymysql
import traceback
import Config
import time

class Connection:

    def __init__(self):
        self.db_connection_MYSQL_Contabo()
        self.max_reintentos = 5
        self.tiempo_espera = 5

    def reconectar(self):
        intentos = 0
        while intentos < self.max_reintentos:
            try:
                print("Intentando reconectar a la base de datos...")
                if self.db is None and self.tunnel is not None:
                    
                    self.db = pymysql.connect(host='127.0.0.1', user=Config.USER_SERVER, database=Config.DATABASE_SERVER,password=Config.PASS_SERVER, port=self.tunnel.local_bind_port)
                    print("Reconectado con éxito.")
                elif self.db is None and self.tunnel is None:
                    self.db,self.tunnel = self.db_connection_MYSQL_Contabo()
                    print("Reconectado con éxito.")
                return True
            except pymysql.err.OperationalError:
                print(f"Fallo la reconexión. Intento {intentos + 1} de {self.max_reintentos}.")
                time.sleep(self.tiempo_espera)
                intentos += 1
        print("No se pudo reconectar a la base de datos.")
        return False

    def db_connection_MYSQL_Contabo(self):
        try:
            self.tunnel = SSHTunnelForwarder((Config.IP_SERVER, int(Config.PORT_SERVER)), 
                                        ssh_password=Config.PASS_SERVER, 
                                        ssh_username=Config.USER_SERVER,
                                        remote_bind_address=("localhost", 3306)) 
            self.tunnel.start()
            #db =  pymysql.connect(host='127.0.0.1', user="db_user", database="db_lupajuridica",password="Lupa-12312423**12", port=tunnel.local_bind_port)
            self.db =   pymysql.connect(host='127.0.0.1', user=Config.USER_SERVER, database=Config.DATABASE_SERVER,password=Config.PASS_SERVER, port=self.tunnel.local_bind_port)
            return self.db,self.tunnel
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return None,None

    def Select_Base(self,Id,CPU,Base,Tipo=0):
        try:
            cursor=self.db.cursor()
            cursor.execute("BEGIN")
            # Seleccionar un registro disponible
            if Tipo == 0:
                cursor.execute(f"SELECT Codigo FROM BASE WHERE Status = '0' AND Machine IS NULL LIMIT {str(int(CPU)**3)}")
                registro = cursor.fetchall()
            elif Tipo == 1:
                if Base is not None and Base != "":
                    cursor.execute(f"SELECT Codigo FROM BASE WHERE Status = '2' AND Name = '{Base}' LIMIT {str(int(CPU)**3)}")
                    registro = cursor.fetchall()
                else:
                    cursor.execute(f"SELECT Codigo FROM BASE WHERE Status = '2' LIMIT {str(int(CPU)**3)}")
                    registro = cursor.fetchall()
            elif Tipo == 2:
                cursor.execute(f"SELECT Codigo FROM BASE WHERE Status = '0' AND Name = '{Base}' AND Machine IS NULL LIMIT {str(int(CPU)**3)}")
                registro = cursor.fetchall()
            registro = [row[0] for row in registro]
            if len(registro) > 0:
                if len(registro)==1:
                    # Actualizar el registro seleccionado
                    Sql=f"UPDATE BASE SET Machine = '{Id}' WHERE Codigo = '{registro[0]}'"
                else:
                    # Actualizar el registro seleccionado
                    Sql=f"UPDATE BASE SET Machine = '{Id}' WHERE Codigo IN {tuple(registro)}"
                cursor.execute(Sql)
                self.db.commit()
                return registro
            else:
                cursor.execute(f"SELECT Codigo FROM BASE WHERE Machine = '{Id}' AND Status = '2' LIMIT {str(int(CPU)**3)}")
                registro = cursor.fetchall()
                registro = [row[0] for row in registro]
                if len(registro) > 0:
                    if len(registro)==1:
                        # Actualizar el registro seleccionado
                        Sql=f"UPDATE BASE SET Machine = '{Id}' WHERE Codigo = '{registro[0]}'"
                    else:
                        # Actualizar el registro seleccionado
                        Sql=f"UPDATE BASE SET Machine = '{Id}' WHERE Codigo IN {tuple(registro)}"
                    cursor.execute(Sql)
                    self.db.commit()
                    return registro
                else:
                    self.db.rollback()
                    return None
        except Exception as e:
            self.db.rollback()
            print(e)
            print(traceback.format_exc())
            return None

    def Actualizar_Proceso(self,data):
        try:
            cursor = self.db.cursor()
            cursor.execute("BEGIN")
            Sql="UPDATE BASE SET "
            if "Status" in data and data['Status'] is not None and data['Status'] != "":
                Sql+=f" Status = '{data['Status']}',"
            if "Machine" in data and data['Machine'] is not None and data['Machine'] != "":
                Sql+=f" Machine = '{data['Machine']}',"
            Sql=Sql[:-1]
            if len(data['Procesos'])==1:
                Sql+=f" WHERE Codigo = '{data['Procesos'][0]}'"
            else:
                registro = [row for row in data['Procesos']]
                # If there are multiple registros, format it as a tuple
                in_clause = str(tuple(registro))
                Sql+=f" WHERE Codigo in  {in_clause}"
            cursor.execute(Sql)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            print(traceback.format_exc())
            return False

    def Select_Agente(self,Id):
        try:
            cursor = self.db.cursor()
            cursor.execute(f"""SELECT Guid,Status,Name,Hostname,IP,IPV4,IPV6,Fecha,FechaUpdate,Ram,Usuario,Descarga,Subida,CPU,Ubicacion,Tipo,Base FROM AGENTE WHERE Guid = '{Id}'""")
            result = cursor.fetchone()
            cursor.close()
            #convertir result json
            if result is not None:
                result = {
                    "Guid":str(result[0]),
                    "Status":str(result[1]),
                    "Name":result[2],
                    "Hostname":result[3],
                    "IP":str(result[4]),
                    "IPV4":str(result[5]),
                    "IPV6":str(result[6]),
                    "Fecha":str(result[7]),
                    "FechaUpdate":str(result[8]),
                    "Ram":str(result[9]),
                    "Usuario":str(result[10]),
                    "Descarga":str(result[11]),
                    "Subida":str(result[12]),
                    "CPU":str(result[13]),
                    "Ubicacion":str(result[14]),
                    "Tipo":str(result[15]),
                    "Base":str(result[16])

                }
                return result
            else:
                return None
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return None

    def close(self):
        self.tunnel.close()
        self.db.close()
        return True        