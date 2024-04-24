import datetime
import traceback

class EvidenciaClass:
    def __init__(self):
        pass

    def printr(self,message):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


    def InsertProceso(self,Proceso,db):
            Sql=f"""INSERT INTO Evidencias (Codigo,Date,File,Verify) VALUES (%s,%s,%s,%s);
                """
            try:
                #print(Sql)
                db.ping()
                cursor = db.cursor()
                cursor.execute(Sql,Proceso)
                db.commit()
                self.printr(f"{Proceso[0]} Evidencia Insertada")
                return True
            except Exception as e:
                if not "Duplicate entry" in str(e):
                    self.printr(f"{Proceso[0]} Error: {e}")
                    return False
                else:
                    self.printr(f"{Proceso[0]} Evidencia Duplicada")
                    return True
        