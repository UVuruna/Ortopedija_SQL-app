from A_Variables import *
from B_Decorators import password,error_cathcer
from C_GoogleDrive import GoogleDrive_User

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
        print(f"__INITIALIZING__ {Database}")
        self.Admin = False
        self.GodMode = False
        self.database = database

        self.connection = None
        self.cursor = None
        self.QUERY = str()

        # KOLONE TABELA
        self.MKB = self.show_columns('mkb10 2010')[1:]        
        self.patient = self.show_columns('pacijenti')[1:]
        self.diagnose = self.show_columns('pacijenti dijagnoza')[-2:]
        self.operation = self.show_columns('operaciona lista')[1:]
        self.slike = self.show_columns('slike')[2:-1]
        self.logs = self.show_columns('logs')[1:-2]
        print(self.logs)

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

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

    @error_cathcer
    def select(self, table, *args, **kwargs):
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
                self.QUERY = query

            self.cursor.execute(query)
            view = self.cursor.fetchall()
            
            query = self.format_sql(query)
            print('----'*66)
            print(query)
            print('----'*66)
            return view,query
        finally:
            self.close_connection()
            
    @error_cathcer
    def join_select(self, table, *args, **kwargs):
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
                self.QUERY = query

            self.cursor.execute(query)
            view = self.cursor.fetchall()

            query = self.format_sql(query)
            return view,query
        finally:
            self.close_connection()
            
    
    def show_columns(self,table):
        try:
            self.connect()
            table = f"`{table}`" if " " in table else table
            query = f"PRAGMA table_info({table})"

            self.cursor.execute(query)
            table = self.cursor.fetchall()
            return [i[1] for i in table]
        finally:
            self.close_connection()
            
    @error_cathcer
    def filter(self,columns):
        if not self.QUERY or 'FROM pacijenti' not in self.QUERY:
            return
        try:
            self.connect()
            wherenull = "WHERE "
            for k,v in columns.items():
                null = "IS NOT NULL" if v else "IS NULL"
                txt = f'`{k}`' if ' ' in k else k
                wherenull += f"pacijenti.{txt} {null} AND "
            wherenull = wherenull.rstrip(" AND ")

            if 'WHERE' in self.QUERY:
                fix = self.QUERY.split("WHERE")
                query = fix[0]+f"{wherenull} AND "+fix[1]
            elif 'GROUP BY' in self.QUERY:
                fix = self.QUERY.split("GROUP BY")
                query = fix[0]+f"{wherenull} GROUP BY"+fix[1]
            else:
                query = self.QUERY+f" {wherenull}"

            self.cursor.execute(query)
            view = self.cursor.fetchall()

            query = self.format_sql(query)
            return view,query
        finally:
            self.close_connection()
            

    def patient_data(self,ID):
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
            

    def execute_selectquery(self,query):
        try:
            self.connect()
            self.cursor.execute(query)
            view = self.cursor.fetchall()
            return view
        finally:
            self.close_connection()
            

    def execute_Update(self,table,id:tuple,**kwargs):
        try:
            self.connect()
            settin = ""
            value = []
            for k,v in kwargs.items():
                txt = k if " " not in k else f"`{k}`"
                settin += f"{txt} = ?, "
                value.append(v)
            settin = settin.rstrip(", ")
            value.append(id[1])
            value = tuple(value)

            table = table if " " not in table else f"`{table}`"
            query = f"UPDATE {table} SET {settin} WHERE {id[0]} = ?"
            self.cursor.execute(query,value)
            self.connection.commit()
        finally:
            self.close_connection()
    
    def execute_Insert(self,table,**kwargs):
        try:
            self.connect()
            counter = 0
            columns = ""
            values = []
            for k,v in kwargs.items():
                txt = k if " " not in k else f"`{k}`"
                columns+= f"{txt}, "
                values.append(v)
                counter+=1
            columns = columns.rstrip(", ")
            values = tuple(values)

            table = table if " " not in table else f"`{table}`"
            query = f"INSERT INTO {table} ({columns}) VALUES ({("?, "*counter).rstrip(", ")})"
            print(query)
            self.cursor.execute(query,values)
            self.connection.commit()
        finally:
            self.close_connection()
    
    def execute_Delete(self,table,id):
        try:
            self.connect()
            table = table if " " not in table else f"`{table}`"
            query = f"DELETE FROM {table} WHERE {id[0]} = {id[1]}"
            self.cursor.execute(query)
            self.connection.commit()
        finally:
            self.close_connection()

    def get_imageBlob(self,id):
        try:
            self.connect()
            query = f"SELECT image_data FROM slike WHERE id_slike = {id}"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                return result[0]
        finally:
            self.close_connection()

    def Vaccum_DB(self):
        try:
            self.connect()
            self.cursor.execute("VACUUM")
        finally:
            self.close_connection()

if __name__=='__main__':

    #'''
    rhmh = Database('RHMH.db')
    table = rhmh.execute_selectquery("SELECT * FROM logs")
    for i in table:
        if i[4]=='Success':
            continue
        print()
        for j in i:
            print(j)

    '''
    rhmh.connect()
    query = """CREATE TABLE logs (
                id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                Time TEXT NOT NULL,
                Query TEXT NOT NULL,
                Error TEXT DEFAULT 'Success',
                `Full Query` TEXT NOT NULL,
                `Full Error` TEXT
            );"""
    
    
    rhmh.cursor.execute("DROP TABLE IF EXISTS logs")
    rhmh.cursor.execute(query)
    rhmh.close_connection()

    rhmh.Vaccum_DB()
    #'''

    #user = GoogleDrive_User()
    #user.update_file(RHMH_DB['id'],"RHMH.db",RHMH_DB['mime'])






