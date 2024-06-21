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
        self.MKB = self.show_columns('mkb10 2010')[1:]        
        self.patient = self.show_columns('pacijenti')[1:]
        self.diagnose = self.show_columns('pacijenti dijagnoza')[-2:]
        self.operation = self.show_columns('operaciona lista')[1:]
        self.slike = self.show_columns('slike')[2:-1]
        self.logs = self.show_columns('logs')[:-2]
        self.session = self.show_columns('session')[1:]

    def GodMode_Password(self,event,parent,notebook:tb.Notebook):
        if not self.Admin:
            dialog = PasswordDialog(parent, "GodMode Unlocking...")
            if dialog.password=='666':
                self.Admin = True
                notebook.execute_select(3)
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
            if "Dg" in col:
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
            try:
                self.connect()
                table = f"`{table}`" if " " in table else table       
                select_values = ",".join(f"`{a}`" if ' ' in a else a for a in args)
                where_pairs = ""
                    
                for k,v in kwargs.items():
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
                    if val in self.diagnose:
                        joindiagnose = True
                        select_values += f"GROUP_CONCAT(CASE WHEN `pacijenti dijagnoza`.{TXT}=1 THEN `mkb10 2010`.`MKB - šifra` END) AS {TXT},"
                    elif val in self.operation:
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
                    if k in self.diagnose:
                        joindiagnose = True
                        col = f"`pacijenti dijagnoza`.{TXT}"
                    elif k in self.operation:
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
                    join_tables += f"JOIN `pacijenti dijagnoza` ON {table}.id_pacijent = `pacijenti dijagnoza`.id_pacijent " + \
                                    f"JOIN `mkb10 2010` ON `pacijenti dijagnoza`.id_dijagnoza = `mkb10 2010`.id_dijagnoza "
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
                #wherenull = wherenull.rstrip(" AND ")

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
                for col in self.patient:
                    SELECT += "pacijenti."
                    SELECT += f"`{col}`, " if " " in col else f"{col}, "
                for col in self.diagnose:
                    TXT = f"`{col}`" if " " in col else col
                    SELECT += f"GROUP_CONCAT(DISTINCT CASE WHEN `pacijenti dijagnoza`.{TXT}=1 THEN `mkb10 2010`.`MKB - šifra` END) AS {TXT}, "
                for col in self.operation:
                    SELECT += "`operaciona lista`."
                    SELECT += f"`{col}`, " if " " in col else f"{col}, "
                SELECT += "GROUP_CONCAT(DISTINCT slike.Naziv) AS Slike"

                diagnosejoin = f"JOIN `pacijenti dijagnoza` ON pacijenti.id_pacijent = `pacijenti dijagnoza`.id_pacijent " + \
                                    f"JOIN `mkb10 2010` ON `pacijenti dijagnoza`.id_dijagnoza = `mkb10 2010`.id_dijagnoza "
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
            finally:
                self.close_connection()
    
    #@method_efficency
    #@error_catcher
    def execute_Delete(self,table,id):
        with self.lock:
            try:
                self.connect()
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
    from C_GoogleDrive import GoogleDrive
    #'''
    rhmh = Database('RHMH.db')

    print(rhmh.logs)
    print(rhmh.session)

    table = rhmh.execute_selectquery("SELECT * from logs")
    for i in table:
        for j in i:
            print(j)

    '''
    rhmh.connect()
    query = """CREATE TABLE logs (
                `ID Time` TEXT PRIMARY KEY NOT NULL,
                Email TEXT NOT NULL,
                Query TEXT NOT NULL,
                Error TEXT DEFAULT 'Success',
                `Full Query` TEXT,
                `Full Error` TEXT
            );"""
    
    
    rhmh.cursor.execute("DROP TABLE IF EXISTS logs")
    rhmh.cursor.execute(query)

    #'''
    '''
    query2 = """CREATE TABLE session (
                id_session INTEGER PRIMARY KEY AUTOINCREMENT,
                Email TEXT NOT NULL,
                `Logged IN` TEXT NOT NULL,
                `Logged OUT` TEXT NOT NULL,
                `Session Length` TEXT NOT NULL,
                Searching INTEGER,
                `Searching efficency` INTEGER,
                Modifying INTEGER,
                `Modifying efficency` INTEGER,
                Download INTEGER,
                `Download efficency` INTEGER,
                Upload INTEGER,
                `Upload efficency` INTEGER
            );"""
    
    rhmh.connect()
    rhmh.cursor.execute("DROP TABLE IF EXISTS session")
    rhmh.cursor.execute(query2)
    rhmh.close_connection()

    rhmh.Vaccum_DB()
    #'''

    #user = GoogleDrive()
    #user.upload_UpdateFile(RHMH_DB['id'],"RHMH.db",RHMH_DB['mime'])
