from A_Variables import *
from B_Decorators import password,error_catcher,method_efficency
from C_GoogleDrive import GoogleDrive

class PasswordDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.password = None
        super().__init__(parent, title)

    def body(self, master):
        self.password_entry = tb.Entry(master, show="*")
        self.password_entry.grid(row=0, column=1, padx=10, pady=10)
        return self.password_entry

    def apply(self):
        self.password = self.password_entry.get()

class Database:
    def __init__(self,database) -> None:
        self.GD = GoogleDrive()
        self.Admin = False
        self.GodMode = False
        self.database = database
        self.UserSession = dict()

        self.connection = None
        self.cursor = None
        self.PatientQuery = str()
        self.LoggingQuery = None

        self.lock = threading.Lock()

        # KOLONE TABELA
        self.mkb10 = self.show_columns('mkb10 2010')[1:]        
        self.pacijenti = self.show_columns('pacijenti')[1:]
        self.pacijenti_dijagnoza = self.show_columns('pacijenti dijagnoza')[-2:]
        self.operaciona_lista = self.show_columns('operaciona lista')[1:]
        self.slike = self.show_columns('slike')[2:-1]
        self.logs = self.show_columns('logs')[:-2]
        self.session = self.show_columns('session')[1:]

    def GodMode_Password(self,event,parent,notebook:tb.Notebook):
        if not self.Admin:
            dialog = PasswordDialog(parent, "GodMode Unlocking...")
            if dialog.password=='666':
                self.Admin = True
                notebook.select(3)
            elif dialog.password==password():
                self.Admin = True
                self.GodMode = True
        else:
            txt = "GodMode" if self.GodMode else "Admin"
            dialog = PasswordDialog(parent, f"{txt} Removing...")
            if dialog.password=='33':
                self.Admin = False
                self.GodMode = False

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def show_columns(self,table):
        with self.lock:
            try:
                self.connect()
                table = f"`{table}`" if " " in table else table
                query = f"PRAGMA table_info({table})"

                self.cursor.execute(query)
                table = self.cursor.fetchall()
                return [i[1] for i in table]
            finally:
                self.close_connection()

    def format_sql(self,query):
        formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted_query

    def creating_where_part(self,col,value,andor):
        if isinstance(value,tuple) and len(value)==2:
            return f"( {col} BETWEEN '{value[0]}' AND '{value[1]}' ) {andor} "
        elif isinstance(value,tuple) and len(value)==1:
            if col in self.pacijenti_dijagnoza:
                return f"( `mkb10 2010`.`MKB - šifra` LIKE '%{value[0]}%' AND {col} = 1 ) {andor} "
            else:
                return f"{col} LIKE '%{value[0]}%' {andor} "
        else:
            return f"{col}='{value}' {andor} "
        

    #@method_efficency
    #@error_catcher  
    def execute_selectquery(self,query):
        with self.lock:
            try:
                self.connect()
                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher
    def execute_select(self, table, *args, **kwargs):
        with self.lock:
            print("KWARGS")
            try:
                self.connect()
                table = f"`{table}`" if " " in table else table       
                select_values = ",".join(f"`{a}`" if ' ' in a else a for a in args)
                where_pairs = ""
  
                for k,v in kwargs.items():
                    if v:
                        col = f"`{k}`" if ' ' in k else k
                        if isinstance(v,set):
                            where_pairs += "( "
                            for val in v:
                                where_pairs += self.creating_where_part(col,val,"OR")
                            where_pairs = where_pairs.rstrip(' OR ') + " ) AND "
                        else:
                            where_pairs += self.creating_where_part(col,v,"AND")
                where_pairs = where_pairs.rstrip(" AND ")
                
                query = f"SELECT {select_values} FROM {table}"
                if where_pairs:
                    print(where_pairs)
                    query += f" WHERE {where_pairs}"
                
                if 'FROM pacijenti' in query:
                    self.PatientQuery = query

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher        
    def execute_join_select(self, table, *args, **kwargs):
        with self.lock:
            try:
                self.connect()
                table = f"`{table}`" if " " in table else table
                select_values = ''
                joindiagnose = False
                joinoperation = False
                for val in args:
                    TXT = f"`{val}`" if " " in val else val
                    if val in self.pacijenti_dijagnoza:
                        joindiagnose = True
                        select_values += f"GROUP_CONCAT(CASE WHEN `pacijenti dijagnoza`.{TXT}=1 THEN `mkb10 2010`.`MKB - šifra` END) AS {TXT},"
                    elif val in self.operaciona_lista:
                        joinoperation = True
                        select_values += f"`operaciona lista`.{TXT},"
                    else:
                        select_values += f"{table}.{TXT},"
                select_values = select_values.rstrip(",")

                where_pairs = ""
                    
                for k,v in kwargs.items():
                    if 'Dg' in k:
                        joindiagnose = True
                    TXT = f"`{k}`" if " " in k else k
                    if k in self.pacijenti_dijagnoza:
                        joindiagnose = True
                        col = f"`pacijenti dijagnoza`.{TXT}"
                    elif k in self.operaciona_lista:
                        joinoperation = True
                        col = f"`operaciona lista`.{TXT}"
                    else:
                        col = f"{table}.{TXT}"

                    if isinstance(v,set):
                        where_pairs += "( "
                        for val in v:
                            where_pairs += self.creating_where_part(col,val,"OR")
                        where_pairs = where_pairs.rstrip(' OR ') + " ) AND "
                    else:
                        where_pairs += self.creating_where_part(col,v,"AND")
                where_pairs = where_pairs.rstrip(" AND ")

                join_tables = ""
                if joindiagnose:
                    join_tables += f"LEFT JOIN `pacijenti dijagnoza` ON {table}.id_pacijent = `pacijenti dijagnoza`.id_pacijent " + \
                                    f"LEFT JOIN `mkb10 2010` ON `pacijenti dijagnoza`.id_dijagnoza = `mkb10 2010`.id_dijagnoza "
                if joinoperation:
                    join_tables += f"LEFT JOIN `operaciona lista` ON {table}.id_pacijent = `operaciona lista`.id_pacijent "

                query = f"SELECT {select_values} FROM {table} {join_tables} "
                if where_pairs:
                    query += f" WHERE {where_pairs}"
                query += f" GROUP BY {table}.id_pacijent"

                if 'FROM pacijenti' in query:
                    self.PatientQuery = query

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher        
    def execute_filter_select(self,columns):
        with self.lock:
            if not self.PatientQuery or 'FROM pacijenti' not in self.PatientQuery:
                return
            try:
                self.connect()
                wherenull = "WHERE "
                for k,v in columns.items():
                    null = "IS NOT NULL" if v else "IS NULL"
                    txt = f'`{k}`' if ' ' in k else k
                    wherenull += f"pacijenti.{txt} {null} AND "
                wherenull = wherenull.rstrip(" AND ")

                if 'WHERE' in self.PatientQuery:
                    fix = self.PatientQuery.split("WHERE")
                    query = fix[0]+f"{wherenull} AND "+fix[1]
                elif 'GROUP BY' in self.PatientQuery:
                    fix = self.PatientQuery.split("GROUP BY")
                    query = fix[0]+f"{wherenull} GROUP BY"+fix[1]
                else:
                    query = self.PatientQuery+f" {wherenull}"

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher
    def get_patient_data(self,ID):
        with self.lock:
            try:
                self.connect()
                SELECT = ""
                for col in self.pacijenti:
                    SELECT += "pacijenti."
                    SELECT += f"`{col}`, " if " " in col else f"{col}, "
                for col in self.pacijenti_dijagnoza:
                    TXT = f"`{col}`" if " " in col else col
                    SELECT += f"GROUP_CONCAT(DISTINCT CASE WHEN `pacijenti dijagnoza`.{TXT}=1 THEN `mkb10 2010`.`MKB - šifra` END) AS {TXT}, "
                for col in self.operaciona_lista:
                    SELECT += "`operaciona lista`."
                    SELECT += f"`{col}`, " if " " in col else f"{col}, "
                SELECT += "GROUP_CONCAT(DISTINCT slike.Naziv) AS Slike"

                diagnosejoin = f"LEFT JOIN `pacijenti dijagnoza` ON pacijenti.id_pacijent = `pacijenti dijagnoza`.id_pacijent " + \
                                    f"LEFT JOIN `mkb10 2010` ON `pacijenti dijagnoza`.id_dijagnoza = `mkb10 2010`.id_dijagnoza "
                operationjoin = f"LEFT JOIN `operaciona lista` ON pacijenti.id_pacijent = `operaciona lista`.id_pacijent "
                slikejoin = f"LEFT JOIN slike ON pacijenti.id_pacijent = slike.id_pacijent"
                JOIN = diagnosejoin+operationjoin+slikejoin

                query = f"SELECT {SELECT} FROM pacijenti {JOIN} " + \
                        f"WHERE pacijenti.id_pacijent = {ID} GROUP BY pacijenti.id_pacijent"

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                column_names = [desc[0] for desc in self.cursor.description]
                DICTY = {}
                for col,val in zip(column_names,view[0]):
                    if val:
                        if col=='Slike':
                            if ',' in val:
                                LIST = val.split(',')
                                val = []
                                for i in LIST:
                                    val.append(i)
                            else:
                                val = [val]
                        DICTY[col] = val
                return DICTY
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher        
    def execute_Update(self,table,id:tuple,**kwargs):
        with self.lock:
            try:
                self.connect()
                settin = ""
                loggin = ""
                value = []
                for k,v in kwargs.items():
                    txt = k if " " not in k else f"`{k}`"
                    settin += f"{txt} = ?, "
                    loggin += f"{txt} = {v}, "
                    value.append(v)
                settin = settin.rstrip(", ")
                loggin = loggin.rstrip(", ")
                value.append(id[1])
                value = tuple(value)

                table = table if " " not in table else f"`{table}`"
                logginquery = f"UPDATE {table} SET {loggin} WHERE {id[0]} = {id[1]}"
                query = f"UPDATE {table} SET {settin} WHERE {id[0]} = ?"

                self.LoggingQuery = self.format_sql(logginquery)
                self.cursor.execute(query,value)
                self.connection.commit()
            finally:
                self.close_connection()
    
    #@method_efficency
    #@error_catcher
    def execute_Insert(self,table,**kwargs):
        with self.lock:
            try:
                self.connect()
                counter = 0
                columns = ""
                loggin = ""
                values = []
                for k,v in kwargs.items():
                    if v:
                        txt = k if " " not in k else f"`{k}`"
                        columns += f"{txt}, "
                        loggin += f"{v}, "
                        values.append(v)
                        counter+=1
                columns = columns.rstrip(", ")
                loggin = loggin.rstrip(", ")
                values = tuple(values)

                table = table if " " not in table else f"`{table}`"
                query = f"INSERT INTO {table} ({columns}) VALUES ({("?, "*counter).rstrip(", ")})"
                logginquery = f"INSERT INTO {table} ({columns}) VALUES ({loggin})"

                self.LoggingQuery = self.format_sql(logginquery)
                self.cursor.execute(query,values)
                self.connection.commit()
                self.cursor.execute("SELECT last_insert_rowid()")
                return self.cursor.fetchone()[0]
            finally:
                self.close_connection()
    
    #@method_efficency
    #@error_catcher
    def execute_Delete(self,table,id):
        with self.lock:
            try:
                self.connect()
                self.cursor.execute("PRAGMA foreign_keys=ON")
                table = table if " " not in table else f"`{table}`"
                query = f"DELETE FROM {table} WHERE {id[0]} = {id[1]}"

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                self.connection.commit()
            finally:
                self.close_connection()

    #@method_efficency
    #@error_catcher
    #'''
    def get_imageBlob(self,id):
        with self.lock:
            try:
                self.connect()
                query = f"SELECT image_data FROM slike WHERE id_slike = {id}"
                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                if result:
                    return result[0]
            finally:
                self.close_connection()
                #'''

    def Vaccum_DB(self):
        with self.lock:
            try:
                self.connect()
                self.cursor.execute("VACUUM")
            finally:
                self.close_connection()

if __name__=='__main__':
    rhmh = Database('RHMH.db')

    table = rhmh.execute_selectquery("SELECT * from pacijenti")
    for i,v in enumerate(table[-10:]):
        print(v)

    table = rhmh.execute_selectquery("SELECT * from `pacijenti dijagnoza`")
    for i,v in enumerate(table[-10:]):
        print(v)

    table = rhmh.execute_selectquery("SELECT * from slike")
    for i,v in enumerate(table[-10:]):
        print(v)

    table = rhmh.execute_selectquery("SELECT * from `operaciona lista`")
    for i,v in enumerate(table[-10:]):
        print(v)