from A_Variables import *
from B_Decorators import Singleton
from C_GoogleDrive import GoogleDrive_User
import D_SQLite_Connection as SQLLite
from F_Media_Manipulation import Media

class Buttons(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            print(f"__INITIALIZING__ {Buttons}")
            #self.DB = Database("localhost","root","33666","ortopedija")
            self.DB = SQLLite.Database('RHMH.db')
            self.GD = GoogleDrive_User()
            self.UPDATE = False
            self.NoteBook:tb.Notebook = None
            self.Slike_HideTable: Frame = None

            self.MessageBoxParent: Frame = None
            self.PatientFocus_ID = None
            self.Table_Slike:tb.ttk.Treeview = None
            self.Slike_Viewer:Canvas = None
            self.ValidationState:bool = True

            self.FormTitle = None
            self.PatientInfo = None
            self.Patient_FormVariables = dict()
            self.MKB_FormVariables = dict()
            self.FilterOptions = dict()
            self.FilterButtons = None
            self.MKB_all = None

            Buttons._initialized=True
        
    def format_date(self,date_str,inp,out):
        return datetime.strptime(str(date_str),inp).strftime(out)
    
    def is_date(self,date_string):
        try:
            datetime.strptime(str(date_string), '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def empty_widget(self,widget):
        if isinstance(widget, StringVar) or \
            isinstance(widget, tb.Combobox):
            widget.set('')
        elif isinstance(widget, Text):
            widget.delete("1.0", END)
        elif isinstance(widget, widgets.DateEntry):
            widget.entry.delete(0,END)
        elif isinstance(widget, tb.Entry):
            widget.delete(0,END)
        elif isinstance(widget, tb.Treeview):
            for item in widget.get_children():
                widget.delete(item)
        elif isinstance(widget,tb.Label):
            widget.config(text="")

    def Clear_Form(self):
        self.PatientFocus_ID = None
        self.FormTitle[0].configure(bootstyle=self.FormTitle[1])
        self.PatientInfo.config(text="")
        for widget in self.Patient_FormVariables.values():
            self.empty_widget(widget)

    def Add_Patient(self):
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return

    def add_MKB(self):
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return

    def get_widget_value(self,widget,idx):
        if isinstance(widget, StringVar):
            return widget.get()
        elif isinstance(widget, Text):
            return widget.get("1.0", END).strip()
        elif isinstance(widget, widgets.DateEntry):
            return widget.entry.get()
        elif isinstance(widget, tb.Treeview):
            values = []
            for child in widget.get_children():
                values.append(widget.item(child, 'values')[idx])
            return values
        else:
            return None
        
    def set_widget_value(self,widget,value):
        if self.is_date(value):
            value = self.format_date(value,"%Y-%m-%d","%d-%b-%y")
        if isinstance(widget, StringVar):
            widget.set(value)
        elif isinstance(widget, Text):
            widget.delete("1.0", END)
            widget.insert("1.0", value)
        elif isinstance(widget, widgets.DateEntry):
            widget.entry.delete(0,END)
            widget.entry.insert(0,value)
        elif isinstance(widget, tb.Treeview):
            for item in widget.get_children():
                widget.delete(item)
            if len(value)!=0:
                for i,value in enumerate(value):
                    row = [i+1,value]
                    widget.insert('', END, values=row)

    def Update_Patient(self):
        report = "You didn't make changes.\nUpdate unsuccessful !!!"
        patient = self.DB.patient_data(self.PatientFocus_ID)
        update_Dict = {}
        insert_Dict = {}
        delete_Dict = {}
        report_Dict = {}
 
        if patient:
            PATIENT = f"{patient['Ime']} {patient['Prezime']} ({self.format_date(patient["Datum Prijema"],"%Y-%m-%d","%d-%b-%y")})" 
            for col,widget in self.Patient_FormVariables.items():
                try:
                    old_value = patient[col]
                except KeyError:
                    old_value = ""
                if self.is_date(old_value):
                    old_value = self.format_date(old_value,"%Y-%m-%d","%d-%b-%y")
                new_value = self.get_widget_value(widget,1)
                if not((isinstance(old_value,list) and new_value==old_value) or new_value==str(old_value)):
                    report_Dict[col] = {"New":new_value,"Old":str(old_value)}
                    if col in ["Dg Glavna","Dg Sporedna"]:
                        old = [i.strip() for i in old_value.split(',')]
                        new = [i.strip() for i in new_value.split(',')]
                        INSERT = list(set(new)-set(old))
                        DELETE = list(set(old)-set(new))
                        if DELETE[0]:
                            delete_Dict[col] = DELETE
                        if INSERT[0]:
                            insert_Dict[col] = INSERT
                    else:
                        if col in ["Operator","Anesteziolog","Anestetičar","Asistenti","Gostujući Specijalizanti"]:
                            new_value = " , ".join([i.strip() for i in new_value.split(',')])
                        update_Dict[col] = new_value
            if report_Dict and self.ValidationState:
                report = f"{PATIENT}\n"
                report += '_'*50+'\n'
                for k,v in report_Dict.items():
                    report += f"\t{k}\nNEW: {v['New']}\n"
                    report += f"OLD: {v["Old"]}\n" if v['Old'] else ""
                else:
                    confirmation = Messagebox.yesnocancel(parent=self.MessageBoxParent,
                                    title=f"Do You Want to Process Update?", message=report[:-1], alert=True)

            elif not self.ValidationState:
                report = "You have entered incorrect data.\nUpdate unsuccessful !!!"
        else:
            report = "You didn't select Patient.\nUpdate unsuccessful !!!"

        try:
            if confirmation=="Yes":
                print("YES")
                self.UPDATE = True
            elif confirmation=="No":
                print("No")
            elif confirmation=="Cancel":
                print("CANCEL")
            else:
                print("NONE")
        except UnboundLocalError:
            Messagebox.show_error(parent=self.MessageBoxParent ,title="Update", message=report)
        return
    
    def update_MKB(self):
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return

    def Delete_Patient(self):
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return
    
    def delete_MKB(self):
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return
    
    def import_many_MKB(self):
        self.UPDATE = True
        print("MORA CSV")

    def add_ImageToCanvas(self,event=None,root=None,ID=None):
        if ID is None:
            try:
                ID = self.Table_Slike.item(self.Table_Slike.focus())['values'][1].split("_")[0]
            except IndexError:
                return

        media,GoogleID = self.DB.execute_selectquery(f"SELECT Format,image_data from slike WHERE id_slike={ID}")[0]

        ### NOTE LOADING IMAGE
        self.Slike_Viewer.delete("all")
        self.Slike_Viewer.unbind("<Button-1>")
        parent_name = self.Slike_Viewer.winfo_parent()
        parent_widget = self.Slike_Viewer.nametowidget(parent_name)

        loading_image = Image.open('C:/Users/vurun/Desktop/App/loading_circle.png')
        resized_image, Width, Height  = Media.resize_image(loading_image, parent_widget.winfo_width(), parent_widget.winfo_height())
        tk_image = ImageTk.PhotoImage(resized_image)
        
        self.Slike_Viewer.configure(width=Width, height=Height)
        self.Slike_Viewer.create_image(0, 0, anchor=NW, image=tk_image)
        self.Slike_Viewer.image = tk_image
        ### NOTE AFTER LOADING SCREEN

        def load_actual_image():
            blob_data = self.GD.get_file_blob(GoogleID)
            if "image" in media:
                image = Media.get_image(blob_data)
                image, Width, Height = Media.resize_image(image, parent_widget.winfo_width(), parent_widget.winfo_height())
                image = ImageTk.PhotoImage(image)

                # Ažuriranje dimenzija Canvas widgeta
                self.Slike_Viewer.configure(width=Width, height=Height)
                self.Slike_Viewer.create_image(0, 0, anchor=NW, image=image)
                self.Slike_Viewer.image = image
                self.Slike_Viewer.bind("<Double-1>",lambda event,image=blob_data: Media.open_image(event,image))
                
            elif "video" in media:
                thumbnail,video_data = Media.create_video_thumbnail(blob_data)
                thumbnail, Width, Height = Media.resize_image(thumbnail, parent_widget.winfo_width(), parent_widget.winfo_height())
                thumbnail = ImageTk.PhotoImage(thumbnail)
                
                self.Slike_Viewer.configure(width=Width, height=Height)
                self.Slike_Viewer.create_image(0, 0, anchor=NW, image=thumbnail)
                self.Slike_Viewer.image = thumbnail
                self.Slike_Viewer.bind("<Button-1>",lambda event,video=video_data: Media.play_video(event,video))
        
        root.after(100,load_actual_image)

    def Add_Image(self):
        self.UPDATE = True
        pass
    def Update_Image(self):
        self.UPDATE = True
        pass                                        
    def Delete_Image(self):
        self.UPDATE = True
        pass
    def Show_Images(self,event,root:Tk):
        ID = self.Patient_FormVariables['Slike'].item(self.Patient_FormVariables['Slike'].focus())['values'][1].split("_")[0]
        self.NoteBook.select(2)

        root.after(5,self.Slike_HideTable.grid_remove)
        def execute():
            self.add_ImageToCanvas(root=root,ID=ID)
        root.after(10,execute)

    def Download_Image(self):
        print('slika loading...')

    def Fill_FromImage(self):
        slika = self.Patient_FormVariables['Slike'].item(self.Patient_FormVariables['Slike'].focus())['values'][1].split("_")
        ID = slika[0]
        OPIS = slika[2]
        
        if 'Operaciona' in OPIS:
            image_blob = self.DB.get_imageBlob(ID)
            data = Media.Image_Reader(image_blob,PRINT=True)
            for col,val in data.items():
                if col not in ["Ime","Prezime","Godište"] and val:
                    if isinstance(val,list):
                        val = " , ".join(val)
                    try:
                        widget = self.Patient_FormVariables[col.title()]
                    except KeyError:
                        continue
                    self.set_widget_value(widget,val)

    def validate_dg(self,x) -> bool:
        if ',' in x:
            mkb = x.split(',')
            for i in mkb:
                fix = i.strip()
                if fix not in self.MKB_all:
                    self.ValidationState = False
                    return False
            else:
                self.ValidationState = True
                return True
        elif x.strip() in self.MKB_all or x=="":
            self.ValidationState = True
            return True
        else:
            self.ValidationState = False
            return False

class DBMS(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            print(f"__INITIALIZING__ {DBMS}")
            self.buttons = Buttons()
            self.GD = GoogleDrive_User()
            self.DB = self.buttons.DB

            self.PatientTable_IDs = list()
            self.Table_Pacijenti: tb.ttk.Treeview = None
            self.Table_Logs: tb.ttk.Treeview = None
            self.Table_MKB: tb.ttk.Treeview = None
            self.Settings_Tab = None
            
            self.TablePacijenti_Columns = tuple(['ID']+self.DB.patient[:5]+self.DB.diagnose+self.DB.patient[5:]+self.DB.operation)
            self.Pacijenti_ColumnVars = {column: IntVar() for column in self.TablePacijenti_Columns}

            self.TableMKB_Columns = tuple(['ID']+self.DB.MKB)
            self.MKB_ColumnVars = {column: IntVar() for column in self.TableMKB_Columns}
            self.buttons.MKB_all = [i[0] for i in self.DB.select("mkb10 2010",*("MKB - šifra",))]

            self.TableSlike_Columns = tuple(['ID']+self.DB.slike)
            self.Slike_ColumnVars = {column: IntVar() for column in self.TableSlike_Columns}

            self.TableLogs_Columns = tuple(['ID']+self.DB.logs)
            self.Logs_ColumnVars = {column: IntVar() for column in self.TableLogs_Columns}

            self.Search_Bar: Frame = None
            self.Search_Bar_ENTRIES = dict()
            self.Search_Bar_ON = 1

            DBMS._initialized=True
    
    def selected_columns(self,columns,table):
        Columns = [column for column, var in columns if var.get()==1]

        table.configure(columns=Columns)
        for i,col in enumerate(Columns):
            table.heading(col, text=col, anchor=W)
            table.column(col, stretch=False)
            if i==0:
                table.column(col, width=40, minwidth=20)
            elif col in ['Veličina']:
                table.column(col, width=60, minwidth=30)
            elif col in ['Pol','Godište','Godine','Starost']:
                table.column(col, width=100, minwidth=50)
            elif col in ['Dg Latinski']:
                table.column(col, width=480, minwidth=270)
            elif col in ['Opis Dijagnoze']:
                table.column(col, width=840)
            elif col in ['Naziv','Gostujući Specijalizanti']:
                table.column(col, width=180, minwidth=120)
            elif col in ['Opis']:
                table.column(col, width=140, minwidth=80)
            elif col in ['Naziv']:
                table.column(col, width=280, minwidth=160)
            else:
                table.column(col, width=130, minwidth=70)
        table['show'] = 'headings'
        return Columns[1:]
    
    def Options(self,n,event):
        search_option = self.Search_Bar_ENTRIES[f'search_option_{n}'].get()
        if search_option == 'Pol':
            for k,v in self.Search_Bar_ENTRIES.items():
                if k==f'search_type_{n}':
                    v.configure(text='=')
                v.grid() if k==f'equal_{n}' or ('search' in k  and k[-1]==str(n)) \
                    else v.grid_remove() if k[-1]==str(n) else None
        elif search_option in ['Godište','Starost']:
            for k,v in self.Search_Bar_ENTRIES.items():
                if k==f'search_type_{n}':
                    v.configure(text='od-do')
                v.grid() if k==f'from_{n}' or k==f'to_{n}' or ('search' in k and k[-1]==str(n))  \
                    else v.grid_remove() if k[-1]==str(n) else None
        elif 'Datum' in search_option:
            for k,v in self.Search_Bar_ENTRIES.items():
                if k==f'search_type_{n}':
                    v.configure(text='od-do')
                v.grid() if ('date' in k or 'search' in k) and k[-1]==str(n) \
                    else v.grid_remove() if k[-1]==str(n) else None
        else:
            for k,v in self.Search_Bar_ENTRIES.items():
                if k==f'search_type_{n}':
                    v.configure(text='≈')
                v.grid() if k==f'like_{n}' or ('search' in k and k[-1]==str(n)) \
                    else v.grid_remove() if k[-1]==str(n) else None

    def fill_TablePacijenti(self,table):
        for i, row in enumerate(table):
            formatted_row = [i+1] + [self.buttons.format_date(str(cell),"%Y-%m-%d","%d-%b-%y") if isinstance(cell, date) \
                                    else "" if str(cell)=="None" \
                                        else cell for cell in row[1:]]
            self.Table_Pacijenti.insert('', END, values=formatted_row)
            self.PatientTable_IDs.append(row[0])

    def fill_Tables_MKB_Logs(self,view,table):
        for i, row in enumerate(view):
            formatted_row = [i+1] + [cell for cell in row]
            table.insert('', END, values=formatted_row)

    def fill_TableSlike(self,table,condition):
        for i, row in enumerate(table):
            if row[0] in condition:
                formatted_row = [i+1] + [f"{cell:,.2f} MB" if isinstance(cell,float) \
                                            else "_".join(cell.split('_')[:2]) if i==0\
                                                else cell for i,cell in enumerate(row[1:])]
                self.buttons.Table_Slike.insert('', END, values=formatted_row)

    def showall_data(self):
        def Result(query_method):
            result = query_method
            error, full_error = None,None
            Time = datetime.now()
            Time = Time.strftime("%Y-%m-%d %H:%M:%S")
            email = self.GD.get_user_email()
            if isinstance(result,dict):
                error = result['Error']
                full_error = result['Full Error']
                full_query = self.DB.QUERY
                full_query = self.DB.format_sql(full_query)
                self.DB.execute_Insert('logs',**{'email':email, 'Time':Time,
                                                 'Error':error, 'Full Error':full_error,
                                                 'Query':"SELECT",'Full Query':full_query})
                return None,None
            else:
                view,query = result
                self.DB.execute_Insert('logs',**{'email':email, 'Time':Time,
                                                 'Query':"SELECT",'Full Query':query})
                return view,query

        focus = self.buttons.NoteBook.index(self.buttons.NoteBook.select())
        if focus==0:
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items(),self.Table_Pacijenti)
            self.PatientTable_IDs.clear()
            
            view, query = Result(self.DB.join_select("pacijenti",*(['id_pacijent']+columns)))
            if self.DB.Admin is True:
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Show All Pacijenti", message=query)
            
            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)
        elif focus==1:
            columns = self.selected_columns(self.MKB_ColumnVars.items(),self.Table_MKB)

            view, query = Result(self.DB.select("mkb10 2010",*(columns)))
            if self.DB.Admin is True:
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Show All MKB10", message=query)

            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_MKB_Logs(view,self.Table_MKB)

        elif focus==2:
            columns = self.selected_columns(self.Slike_ColumnVars.items(),self.buttons.Table_Slike)

            view, query = Result(self.DB.select("slike",*(['id_pacijent']+columns)))
            if self.DB.Admin is True:
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Show All Slike", message=query)

            for item in self.buttons.Table_Slike.get_children():
                self.buttons.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view,self.PatientTable_IDs)

        elif focus==3:
            columns = self.selected_columns(self.Logs_ColumnVars.items(),self.Table_Logs)

            view, query = Result(self.DB.select("logs",*(columns)))
            if self.DB.Admin is True:
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Show All Logs", message=query)

            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_MKB_Logs(view,self.Table_Logs)
        else:
            return

    def search_data(self):
        def searching_dict_create():
            searching = dict()
            for n in range(1,self.Search_Bar_ON+1):
                option = self.Search_Bar_ENTRIES[f"search_option_{n}"].get()
                try:
                    searching[option]
                except KeyError:
                    searching[option] = set()
                if not option:
                    continue
                else:
                    search_type = self.Search_Bar_ENTRIES[f"search_type_{n}"].cget("text")

                if search_type == 'od-do':
                    if 'Datum' in option:
                        searching[option].add((self.buttons.format_date(self.Search_Bar_ENTRIES[f'date_from_{n}'].entry.get(),"%d-%b-%y","%Y-%m-%d"),
                                            self.buttons.format_date(self.Search_Bar_ENTRIES[f'date_to_{n}'].entry.get(),"%d-%b-%y","%Y-%m-%d")))
                    else:
                        searching[option].add((self.Search_Bar_ENTRIES[f'from_{n}'].get(),self.Search_Bar_ENTRIES[f'to_{n}'].get()))
                elif search_type == '=':
                    searching[option].add(self.Search_Bar_ENTRIES[f'equal_{n}'].get())
                else:
                    searching[option].add((self.Search_Bar_ENTRIES[f'like_{n}'].get(),))

            for k,v in searching.items():
                if len(v)==1:
                    searching[k] = list(v)[0]
            return searching

        for element in self.Search_Bar.winfo_children():
            if element.winfo_ismapped():
                if isinstance(element,Entry):
                    if element.get():
                        continue
                    else:
                        return
                elif isinstance(element,widgets.DateEntry):
                    if element.entry.get():
                        continue
                    else:
                        return

        focus = self.buttons.NoteBook.index(self.buttons.NoteBook.select())
        if focus==0:
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items(),self.Table_Pacijenti)
            self.PatientTable_IDs.clear()
            searching = searching_dict_create()

            if self.DB.Admin is False:
                view = self.DB.join_select("pacijenti",*(['id_pacijent']+columns),**searching)
            elif self.DB.Admin is True:
                view,query = self.DB.join_select("pacijenti",*(['id_pacijent']+columns),**searching)
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Search Pacijenti", message=query)

            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)

        elif focus==1:
            columns = self.selected_columns(self.MKB_ColumnVars.items(),self.Table_MKB)
            searching = searching_dict_create()

            if self.DB.Admin is False:
                view = self.DB.select("mkb10 2010",*(columns),**searching)
            elif self.DB.Admin is True:
                view,query = self.DB.select("mkb10 2010",*(columns),**searching)
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Search MKB10", message=query)

            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_MKB_Logs(view,self.Table_MKB)

        elif focus==2:
            columns = self.selected_columns(self.Slike_ColumnVars.items(),self.buttons.Table_Slike)
            searching = searching_dict_create()

            if self.DB.Admin is False:
                view = self.DB.select("slike",*(['id_pacijent']+columns),**searching)
            elif self.DB.Admin is True:
                view,query = self.DB.select("slike",*(['id_pacijent']+columns),**searching)
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Search Slike", message=query)

            for item in self.buttons.Table_Slike.get_children():
                self.buttons.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view,self.PatientTable_IDs)

        elif focus==3:
            columns = self.selected_columns(self.Logs_ColumnVars.items(),self.Table_Logs)
            searching = searching_dict_create()

            if self.DB.Admin is False:
                view = self.DB.select("logs",*(['id_log']+columns),**searching)
            elif self.DB.Admin is True:
                view,query = self.DB.select("logs",*(['id_log']+columns),**searching)
                Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Search Logs", message=query)

            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_MKB_Logs(view,self.Table_Logs)

    def filtered(self,columns):
        where = {}
        self.PatientTable_IDs.clear()
        for k,v in self.buttons.FilterOptions.items():
            if k in columns:
                where[k]=v[1].get()
        
        if self.DB.Admin is False:
            view = self.DB.filter(where)
        elif self.DB.Admin is True:
            view,query = self.DB.filter(where)
            Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Filter Pacijenti", message=query)

        for item in self.Table_Pacijenti.get_children():
            self.Table_Pacijenti.delete(item)
        if view and len(view)!=0:
            for i, row in enumerate(view):
                formatted_row = [i+1] + [self.buttons.format_date(str(cell),"%Y-%m-%d","%d-%b-%y") if isinstance(cell, date) \
                                         else "" if str(cell)=="None" \
                                            else cell for cell in row[1:]]
                self.PatientTable_IDs.append(row[0])
                self.Table_Pacijenti.insert('', END, values=formatted_row)

    def fill_MKBForm(self,event):
        row = self.Table_MKB.item(self.Table_MKB.focus())['values'][1:]
        headings = [column for column, var in self.MKB_ColumnVars.items() if var.get()==1][1:]
        for col,val in zip(headings,row):
            self.buttons.MKB_FormVariables[col].set(val)

    def fill_PatientForm(self,event):
        self.buttons.Clear_Form()
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            self.buttons.PatientFocus_ID = self.PatientTable_IDs[self.Table_Pacijenti.item(self.Table_Pacijenti.focus())['values'][0]-1] 
            patient = self.DB.patient_data(self.buttons.PatientFocus_ID)
        except IndexError:
            return
        for col,val in patient.items():
            try:
                widget = self.buttons.Patient_FormVariables[col]
            except KeyError:
                continue
            self.buttons.set_widget_value(widget,val)
        TEXT = f"{patient["Ime"]} {patient["Prezime"]} "
        try:
            TEXT += f"({self.buttons.format_date(str(patient['Datum Prijema']),"%Y-%m-%d","%d-%b-%y")})"
        except KeyError:
            pass
        self.buttons.PatientInfo.config(text=TEXT)
        self.buttons.FormTitle[0].configure(bootstyle='success')
      
    def tab_change(self,event):
        def filter_buttons_state(state):
            for widget in self.buttons.FilterButtons.winfo_children():
                if isinstance(widget,ctk.CTkButton):
                    widget.configure(state=state)

        def tab_swapping(values,state):
            if not self.Search_Bar.winfo_ismapped():
                self.Search_Bar.grid()
            filter_buttons_state(state)
            for i in range(1,max_searchby+1):
                self.Search_Bar_ENTRIES[f'search_option_{i}'].configure(values=values)
            for Type,Widget in self.Search_Bar_ENTRIES.items():
                self.buttons.empty_widget(Widget)
                if 'search_option' not in Type:
                    if Widget.winfo_ismapped():
                        Widget.grid_remove() 

        focus = self.buttons.NoteBook.index(self.buttons.NoteBook.select())
        if focus==0:
            self.showall_data()
            tab_swapping(self.TablePacijenti_Columns[1:],'normal')
        elif focus==1:
            self.showall_data()
            tab_swapping(self.TableMKB_Columns[1:],'disabled')
        elif focus==2:
            self.showall_data()
            self.buttons.Slike_HideTable.grid()
            tab_swapping(self.TableSlike_Columns[1:],'disabled')
        elif focus==3:
            self.showall_data()
            tab_swapping(self.TableLogs_Columns[1:],'disabled')
        else:
            self.Search_Bar.grid_remove()
        
