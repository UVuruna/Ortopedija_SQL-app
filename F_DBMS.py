from A_Variables import *
from B_Decorators import Singleton
from C_GoogleDrive import GoogleDrive
from E_SQLite import Database
from D_Media import Media

class Buttons(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            Buttons._initialized=True
            self.ROOT:Tk = None
            self.DB = Database('RHMH.db')
            self.GD = GoogleDrive()
            self.DBMS = DBMS()
            self.LoggingQuery = self.DB.LoggingQuery
            self.UPDATE = False
            self.Buttons = dict()
            self.NoteBook:tb.Notebook = None
            self.Slike_HideTable: Frame = None

            self.MessageBoxParent: Frame = None
            self.PatientFocus_ID = None
            self.Table_Slike:tb.ttk.Treeview = None

            self.Validation_Widgets = []
            self.Valid_Dijagnoza:bool = True
            self.Valid_Godiste:bool = True
            self.Valid_Datum:bool = True
            self.Valid_NotBlank:bool = True

            self.FormTitle = None
            self.PatientInfo = None
            self.Patient_FormVariables = {'pacijenti':{},'pacijenti dijagnoza':{},'operaciona lista':{},'slike':{}}
            self.MKB_FormVariables = dict()
            self.Logs_FormVariables = dict()
            self.FilterOptions = dict()
            self.MKB_all = None
    
    def is_DB_date(self,date_string): # Checks if it is DB Date Format
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

    def get_widget_value(self,widget):
        if isinstance(widget, StringVar):
            return widget.get()
        elif isinstance(widget, Text):
            return widget.get("1.0", END).strip()
        elif isinstance(widget, widgets.DateEntry):
            return widget.entry.get()
        else:
            return None
        
    def set_widget_value(self,widget,value):
        if not value:
            return
        if self.is_DB_date(value):
            # DB Date Format TO Form Date Format
            value = datetime.strptime(str(value),"%Y-%m-%d").strftime("%d-%b-%Y")
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

    def Clear_Form(self):
        self.PatientFocus_ID = None
        self.FormTitle[0].configure(bootstyle=self.FormTitle[1])
        self.PatientInfo.config(text="")
        for table_groups in self.Patient_FormVariables.values():
            for widget in table_groups.values():
                self.empty_widget(widget)
    
    def Add_Patient(self):
        if not (self.Valid_Dijagnoza and self.Valid_Datum and self.Valid_Godiste and self.Valid_NotBlank):
            Messagebox.show_warning(parent=self.MessageBoxParent,
                                    title=f"Inserting failed!", message="Wrong data in Patient Form")
            return
        reportDict = {}
        for table in self.Patient_FormVariables.keys():
            insertDict = {}
            if table=='pacijenti':
                trenutna_godina = datetime.now().year
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        if "Datum" in col: # FROM Form Date Format TO DB Date Format
                            value = datetime.strptime(value, "%d-%b-%Y").strftime("%Y-%m-%d")
                            if col=='Datum Prijema':
                                trenutna_godina = datetime.strptime(value, "%Y-%m-%d").year
                        elif col=='Godište':
                            godiste = int(value)
                        insertDict[col] = value
                        reportDict[col] = value
                insertDict['Starost'] = trenutna_godina-godiste
                ID = self.DB.execute_Insert(table,**insertDict)
            elif table == 'pacijenti dijagnoza':
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        value = value.replace(","," ")
                        value = value.split()
                        for mkb in value:
                            insertDict.clear()
                            insertDict['id_pacijent'] = ID
                            insertDict[col] = 1
                            reportDict[col] = mkb
                            insertDict['id_dijagnoza'] = self.DB.execute_selectquery(f'SELECT id_dijagnoza FROM `mkb10 2010` WHERE `MKB - šifra` = "{mkb}"')[0][0]
                            self.DB.execute_Insert(table,**insertDict)
            elif table=='operaciona lista':
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        if "," in value:
                            value = value.split(",")
                            fix = []
                            for doc in value:
                                fix.append(doc.strip())
                            value = (" , ".join(fix))
                        insertDict[col] = value
                        reportDict[col] = value
                insertDict["id_pacijent"] = ID
                self.DB.execute_Insert(table,**insertDict)
        report = ""
        for col,val in reportDict.values():
            report += f"{col}: {val}\n"
        Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f"New Patient added", message=report[:-1], alert=True)

    def Add_MKB(self):
        insertDict = {}
        for col,val in self.MKB_FormVariables.items():
            insertDict[col] = self.get_widget_value(val)

        if len(list(insertDict.keys()))==2:
            self.DB.execute_Insert('mkb10 2010',**insertDict)
            report = ""
            for col,val in insertDict.values():
                report += f"{col}: {val}\n"
            Messagebox.show_info(parent=self.MessageBoxParent,
                        title=f"New MKB added", message=report[:-1], alert=True)
        else:
            Messagebox.show_warning(parent=self.MessageBoxParent,
                                    title=f"Inserting failed!", message="Niste uneli sve tražene podatke")
    
    def Update_Patient(self):
        patient = self.DB.get_patient_data(self.PatientFocus_ID)
        ID_PATIENT = ('id_pacijent',self.PatientFocus_ID)
        update_Dict = {}
        insert_Dict = {}
        delete_Dict = {}

        report_Dict = {}
 
        if patient:
            PATIENT = f"{patient['Ime']} {patient['Prezime']}"
            try:
                # FROM DB Date Formate TO Patient Report Date Format
                datumprijema = f" ({datetime.strptime(str(patient["Datum Prijema"]),"%Y-%m-%d").strftime("%d-%b-%y")})"
                PATIENT += datumprijema
            except KeyError:
                pass

            for table,tabledict in self.Patient_FormVariables.items():
                if table == 'slike':
                    continue
                delete_Dict[table] = {}
                for col,widget in tabledict.items():
                    try:
                        OLD = patient[col]
                        if table=='pacijent' and 'Datum' in col:
                            OLD = datetime.strptime(OLD,"%Y-%m-%d").strftime("%d-%b-%Y")
                    except KeyError:
                        OLD = ""
                    
                    NEW = self.get_widget_value(widget)

                    NEW = ' '.join(str(NEW).split()) # da se srede visak razmaka
                    OLD = ' '.join(str(OLD).split()) # mora str zbog int values
                    if NEW!=OLD:
                        report_Dict[col] = {"New":NEW,"Old":OLD}
                        if table=='pacijenti dijagnoza':
                            old = [i.strip() for i in OLD.split(',')]
                            new = [i.strip() for i in NEW.split(',')]
                            INSERT = set(new)-set(old) ; INSERT.remove("")
                            DELETE = set(old)-set(new) ; DELETE.remove("")
                            if DELETE:
                                delete_Dict[table][col] = DELETE
                            if INSERT:
                                insert_Dict[table][col] = INSERT
                        elif table=='operaciona lista':
                            NEW = " , ".join([i.strip() for i in NEW.split(',')])
                            if OLD:
                                update_Dict[table][col] = NEW
                            else:
                                insert_Dict[table][col] = NEW
                        else: # Table pacijenti
                            if OLD:
                                update_Dict[table][col] = NEW
                            else:
                                insert_Dict[table][col] = NEW

                if report_Dict:
                    if (self.Valid_Dijagnoza and self.Valid_Datum and self.Valid_Godiste and self.Valid_NotBlank):
                        report = f"{PATIENT}\n"
                        for k,v in report_Dict.items():
                            report += f"{k}"
                            report += f"\n  New: {v['New']}\n"
                            if v['Old']:
                                report += f"  Old: {v["Old"]}\n"
                        else:
                            confirmation = Messagebox.yesno(parent=self.MessageBoxParent,
                                            title=f"Do You Want to Process Update?", message=report[:-1], alert=True)
                    else:
                        report = "You have entered incorrect data.\nUpdate failed !!!"
                else:
                    report = "You made no changes to current patient.\nUpdate failed !!!"
        else:
            report = "You didn't select Patient.\nUpdate failed !!!"

        try:
            if confirmation=="Yes":
                print("YES")
                print(update_Dict)
                print(delete_Dict)
                print(insert_Dict)
            elif confirmation=="No":
                print("No")
            else:
                print("NONE")
        except UnboundLocalError:
            Messagebox.show_error(parent=self.MessageBoxParent ,title="Update failed!", message=report)
    
    def Update_MKB(self):
        updateDict = {}
        print(self.MKB_FormVariables)
        for col,val in self.MKB_FormVariables.items():
            updateDict[col] = self.get_widget_value(val)

        mkb = self.DBMS.Table_MKB.item(self.DBMS.Table_MKB.focus())['values'][1]
        ID = self.DB.execute_selectquery(f"SELECT id_dijagnoza from `mkb10 2010` WHERE `MKB - šifra` = {mkb}")

        if len(list(updateDict.keys()))==2:
            self.DB.execute_Update(table='mkb10 2010',id=('id_dijagnoze',ID),**updateDict)
        else:
            Messagebox.show_warning(parent=self.MessageBoxParent,
                                    title=f"Updating failed!", message="Niste uneli sve tražene podatke")
    
    #@method_efficency
    #@error_catcher
    def Delete_Patient(self):
        confirm = Messagebox.yesno(parent=self.MessageBoxParent,
                                title=f"Deleting...", message=f"Are you sure you want to delete\n{self.PatientInfo.cget('text')}?", alert=True)
        if confirm=='Yes':
            self.DB.execute_Delete('pacijenti',('id_pacijent',self.PatientFocus_ID))
            self.Clear_Form()
            self.DBMS.showall_data(0)
            self.UPDATE = True
        return
    
    #@method_efficency
    #@error_catcher
    def Delete_MKB(self):
        print("---"*66)
        self.UPDATE = True
        messagebox.showwarning("Greška","Niste uneli sve tražene podatke!")
        return
    
    def import_many_MKB(self):
        self.UPDATE = True
        print(self.GD.UserSession)

    def Show_Image_execute(self,ID=None,MediaType=None,blob_data=False):
        if blob_data is False:
            blob_data = self.GD.download_BLOB(ID)

        width = Media.Slike_Viewer.winfo_width()
        height = Media.Slike_Viewer.winfo_height()

        if "image" in MediaType:
            Media.Image_Active = Media.get_image(blob_data)
            image = Media.resize_image(Media.Image_Active, width, height, savescale=True)
            image = ImageTk.PhotoImage(image)

            Media.Slike_Viewer.create_image(width//2, height//2,  anchor='center', image=image)
            Media.Slike_Viewer.image = image
            Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
            Media.Slike_Viewer.bind("<Double-1>",lambda event,image_data=blob_data: Media.open_image(event,image_data))
            Media.Slike_Viewer.bind("<MouseWheel>", Media.zoom)
            Media.Slike_Viewer.bind("<Button-4>", Media.zoom)
            Media.Slike_Viewer.bind("<Button-5>", Media.zoom)
            Media.Slike_Viewer.bind('<ButtonPress-1>', Media.move_from)
            Media.Slike_Viewer.bind('<B1-Motion>',     Media.move_to)
            
        elif "video" in MediaType:
            thumbnail,video_data = Media.create_video_thumbnail(blob_data)
            thumbnail = Media.resize_image(thumbnail, width, height)
            thumbnail = ImageTk.PhotoImage(thumbnail)
            
            Media.Slike_Viewer.create_image(width//2, height//2, anchor='center', image=thumbnail)
            Media.Slike_Viewer.image = thumbnail
            Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
            Media.Slike_Viewer.bind("<Button-1>",lambda event,video=video_data: Media.play_video(event,video))

    #@method_efficency
    #@error_catcher
    def Show_Image(self,event=None,ID=False,BLOB=False):
        Media.Slike_Viewer.delete("all")
        Media.Image_Active = None

        if BLOB is False:
            if ID is False:
                try:
                    ID = self.Table_Slike.item(self.Table_Slike.focus())['values'][1].split("_")[0]
                except IndexError:
                    return
            media_type,google_ID = self.DB.execute_selectquery(f"SELECT Format,image_data from slike WHERE id_slike={ID}")[0]

        events = ["<Button-1>","<Double-1>","<MouseWheel>","<Button-4>","<Button-5>","<ButtonPress-1","<B1-Motion>"]
        for event in events:
            Media.Slike_Viewer.unbind(event)
        self.ROOT.update() # CEKA SREDJIVANJE WIDGET

        width = Media.Slike_Viewer.winfo_width()
        height = Media.Slike_Viewer.winfo_height()
        image = Image.open('C:/Users/vurun/Desktop/App/loading_circle.png')
        image = Media.resize_image(image, width, height)
        image = ImageTk.PhotoImage(image)

        Media.Slike_Viewer.create_image(width//2, height//2, anchor='center', image=image)
        Media.Slike_Viewer.image = image
        Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
        
        # AFTER LOADING.. png Actual Image
        if BLOB is False:
            self.ROOT.after(WAIT,
                            lambda ID=google_ID,mediatype=media_type: 
                            self.Show_Image_execute(ID=ID,MediaType=mediatype))
        else:
            self.ROOT.after(WAIT,
                            lambda mediatype='image',blob=BLOB: 
                            self.Show_Image_execute(MediaType=mediatype,blob_data=blob))

    #@method_efficency
    #@error_catcher
    def Add_Image(self):
        print("---"*66)
        self.UPDATE = True
        pass

    #@method_efficency
    #@error_catcher
    def Update_Image(self):
        print("---"*66)
        self.UPDATE = True
        pass   

    #@method_efficency
    #@error_catcher                                     
    def Delete_Image(self):
        print("---"*66)
        self.UPDATE = True
        pass

    def Show_Image_FullScreen(self,event=None,BLOB=None):
        print("---"*66)
        if not BLOB:
            ID = event.widget.item(event.widget.focus())['values'][1].split("_")[0]
            def execute():
                self.Show_Image(ID=ID)
        else:
            def execute():
                self.Show_Image(BLOB=BLOB)
        self.NoteBook.select(2)

        self.ROOT.after(WAIT,self.Slike_HideTable.grid_remove)
        self.ROOT.after(WAIT*2,execute)

    #@method_efficency
    #@error_catcher
    def Image_Read(self, result_queue):
        try:
            data = result_queue.get_nowait()
            report = ""
            for col,val in data.items():
                if val:
                    if isinstance(val,list):
                        val = " , ".join(val) if col not in ["Asistenti","Gostujući Specijalizant"] else ",\n".join(val)
                    for table in self.Patient_FormVariables.keys():
                        try:
                            widget = self.Patient_FormVariables[table][col]
                            break
                        except KeyError:
                            continue
                    report += f"{col}\n  - {val}\n"
                    
                    self.set_widget_value(widget,val)
            else:
                retry = Messagebox.show_question(parent=self.MessageBoxParent ,title="Fill From Image", message=report,
                                         buttons=["Retry:secondary","Ok:primary"])
                if retry == 'Retry':
                    reply = Media.Image_Reader_TryAgain(self.MessageBoxParent)
                    if reply=='Run':
                        self.FillForm_FromImage(firsttry=False)
        except queue.Empty:
            self.ROOT.after(100, self.Image_Read, result_queue)

    #@method_efficency
    #@error_catcher
    def FillForm_FromImage(self,firsttry=True):
        try:
            slika = self.Patient_FormVariables['slike']['Slike'].item(
                    self.Patient_FormVariables['slike']['Slike'].focus()
                    )['values'][1].split('_')
        except IndexError:
            Messagebox.show_error(parent=self.MessageBoxParent,
                    title=f"Fill From Image", message="No image selected!")
            return
        if 'Operaciona' in slika[2]:
            GoogleID = self.DB.execute_selectquery(f"SELECT image_data FROM slike WHERE id_slike = {slika[0]}")[0][0]
            image_blob = self.GD.download_BLOB(GoogleID)

            result_queue = queue.Queue()
            def execute_fullscreen():
                Media.open_image(event=None,image_data=image_blob)
                self.Show_Image_FullScreen(BLOB=image_blob)
            def image_reader_with_queue(image, queue):
                data = Media.Image_Reader(image)
                queue.put(data)

            if firsttry is True:
                t1 = threading.Thread(target=execute_fullscreen)
                t1.start()
            t2 = threading.Thread(target=image_reader_with_queue, args=(image_blob,result_queue))
            t2.start()
            self.Image_Read(result_queue)
        else:
            Messagebox.show_error(parent=self.MessageBoxParent,
                title=f"Fill From Image", message="Image description (Opis)\nhave to be 'Operaciona Lista'")

    def Validation_Method(self,event):
        for widget in self.Validation_Widgets:
            widget:Widget
            widget.focus_force()
        for col,widget in self.Patient_FormVariables['pacijenti'].items():
            if 'Datum' in col:
                if widget:
                    value = self.get_widget_value(widget)
                    if value:
                        try:
                            datetime.strptime(value, "%d-%b-%Y")
                            widget.configure(bootstyle='primary')
                            self.Valid_Datum = True
                        except:
                            widget.configure(bootstyle='danger')
                            self.Valid_Datum = False
                    else:
                        widget.configure(bootstyle='primary')
                        self.Valid_Datum = True
        event.widget.focus_force()

    def validate_notblank(self,x) -> bool:
        if x:
            self.Valid_NotBlank = True
            return True
        else:
            self.Valid_NotBlank = False
            return False        

    def validate_godiste(self,x) -> bool:
        if x.isdigit() and len(x)==4:
            self.Valid_Godiste = True
            return True
        else:
            self.Valid_Godiste = False
            return False

    def validate_dijagnoza(self,x) -> bool:
        if ',' in x:
            mkb = x.split(',')
            for i in mkb:
                fix = i.strip()
                if fix not in self.MKB_all:
                    self.Valid_Dijagnoza = False
                    return False
            else:
                self.Valid_Dijagnoza = True
                return True
        elif x.strip() in self.MKB_all or x=="":
            self.Valid_Dijagnoza = True
            return True
        else:
            self.Valid_Dijagnoza = False
            return False
            

class DBMS(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            DBMS._initialized=True
            self.buttons = Buttons()
            self.GD = GoogleDrive()
            self.DB = self.buttons.DB
            self.LoggingQuery = self.DB.LoggingQuery

            self.PatientTable_IDs = list()
            self.Table_Pacijenti: tb.ttk.Treeview = None
            self.Table_MKB: tb.ttk.Treeview = None

            self.Table_Logs: tb.ttk.Treeview = None
            self.Table_Session: tb.ttk.Treeview = None
            self.Settings_Tab = None
            
            self.TablePacijenti_Columns = tuple(['ID']+self.DB.pacijenti[:5]+self.DB.pacijenti_dijagnoza+self.DB.pacijenti[5:]+self.DB.operaciona_lista)
            self.Pacijenti_ColumnVars = {column: IntVar() for column in self.TablePacijenti_Columns}

            self.TableMKB_Columns = tuple(['ID']+self.DB.mkb10)
            self.MKB_ColumnVars = {column: IntVar() for column in self.TableMKB_Columns}
            self.buttons.MKB_all = [i[0] for i in self.DB.execute_select("mkb10 2010",*("MKB - šifra",))]

            self.TableSlike_Columns = tuple(['ID']+self.DB.slike)
            self.Slike_ColumnVars = {column: IntVar() for column in self.TableSlike_Columns}

            self.TableLogs_Columns = tuple(['ID']+self.DB.logs)
            self.Logs_ColumnVars = {column: IntVar() for column in self.TableLogs_Columns}

            self.TableSession_Columns = tuple(['ID']+self.DB.session)
            self.Session_ColumnVars = {column: IntVar() for column in self.TableSession_Columns}

            self.Search_Bar: Frame = None
            self.Search_Bar_ENTRIES = dict()
            self.Search_Bar_ON = 1

    def selected_columns(self,columns,table:tb.ttk.Treeview):
        Columns = [column for column, var in columns if var.get()==1]

        table.configure(columns=Columns)
        for i,col in enumerate(Columns):
            table.heading(col, text=col, anchor=W)
            table.column(col, stretch=False)
            if i==0: # ID COLUMN
                table.column(col, width=int(F_SIZE*3.6), minwidth=F_SIZE*2)
            elif col in ['Veličina','Views','Modify','Download','Upload']:
                table.column(col, width=int(F_SIZE*6.3), minwidth=F_SIZE*3)
            elif col in ['Pol','Godište','Godine','Starost']:
                table.column(col, width=F_SIZE*9, minwidth=F_SIZE*4)
            elif col in ['Opis']:
                table.column(col, width=F_SIZE*13, minwidth=F_SIZE*6)
            elif col in ['Dg Latinski']:
                table.column(col, width=F_SIZE*43, minwidth=F_SIZE*13)
            elif col in ['Opis Dijagnoze']:
                table.column(col, width=F_SIZE*77)
            elif col in ['Naziv','Gostujući Specijalizant'] or table in [self.Table_Logs,self.Table_Session]:
                table.column(col, width=F_SIZE*16, minwidth=F_SIZE*7)
            else:
                table.column(col, width=130, minwidth=F_SIZE*6)
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
            # FROM DB Date Format TO Table Date Format
            formatted_row = [i+1] + [datetime.strptime(cell,"%Y-%m-%d").strftime("%d-%b-%y") if self.buttons.is_DB_date(cell) \
                                        else " , ".join(cell.split(",")) if isinstance(cell,str) and "," in cell \
                                            else "" if str(cell)=="None" \
                                                else cell for cell in row[1:]]
            self.Table_Pacijenti.insert('', END, values=formatted_row)
            self.PatientTable_IDs.append(row[0])

    def fill_Tables_Other(self,view,table):
        for i, row in enumerate(view):
            formatted_row = [i+1] + [cell for cell in row]
            table.insert('', END, values=formatted_row)

    def fill_TableSlike(self,table,condition=False):
        for i, row in enumerate(table):
            if condition is False or row[0] in condition:
                formatted_row = [i+1] + [f"{cell:,.2f} MB" if isinstance(cell,float) \
                                            else "_".join(cell.split('_')[:2]) if i==0\
                                                else cell for i,cell in enumerate(row[1:])]
                self.buttons.Table_Slike.insert('', END, values=formatted_row)

    def LoggingData(self,result,query_type):
        Time = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.{datetime.now().strftime("%f")[:3]}' 
        if result:
            def execute():
                self.DB.execute_Insert('logs',**{'ID Time':Time, 'Email':self.GD.UserSession['User'],
                                                'Query':query_type,'Full Query':self.DB.LoggingQuery})
            self.buttons.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
        return result

    #@method_efficency
    #@error_catcher
    def showall_data(self,focus=None):
        print("---"*66)
        if focus is None:
            focus = self.buttons.NoteBook.index(self.buttons.NoteBook.select())
        if focus==0:
            self.PatientTable_IDs.clear()
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items(),self.Table_Pacijenti)
            view = self.LoggingData(self.DB.execute_join_select("pacijenti",*(['id_pacijent']+columns)),"Pacijenti All SELECT")
          
            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)

        elif focus==1:
            columns = self.selected_columns(self.MKB_ColumnVars.items(),self.Table_MKB)
            view = self.LoggingData(self.DB.execute_select("mkb10 2010",*(columns)),"MKB All SELECT")
   
            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_MKB)

        elif focus==2:
            columns = self.selected_columns(self.Slike_ColumnVars.items(),self.buttons.Table_Slike)
            view = self.LoggingData(self.DB.execute_select("slike",*(['id_pacijent']+columns)),"Slike All SELECT")

            for item in self.buttons.Table_Slike.get_children():
                self.buttons.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view)

        elif focus==3:
            columns = self.selected_columns(self.Logs_ColumnVars.items(),self.Table_Logs)
            view = self.LoggingData(self.DB.execute_select("logs",*(columns)),"Logs All SELECT")
 
            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Logs)
        
        elif focus==4:
            columns = self.selected_columns(self.Session_ColumnVars.items(),self.Table_Session)
            view = self.LoggingData(self.DB.execute_select("session",*(columns)),"Session All SELECT")

            for item in self.Table_Session.get_children():
                self.Table_Session.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Session)


    #@method_efficency
    #@error_catcher
    def search_data(self):
        print("---"*66)
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
                        # FROM Form Date Formate TO DB Date Format
                        searching[option].add(datetime.strptime(self.Search_Bar_ENTRIES[f'date_from_{n}'].entry.get(),"%d-%b-%Y").strftime("%Y-%m-%d"),
                                            datetime.strptime(self.Search_Bar_ENTRIES[f'date_to_{n}'].entry.get(),"%d-%b-%Y").strftime("%Y-%m-%d"))
                    else:
                        searching[option].add((self.Search_Bar_ENTRIES[f'from_{n}'].get(),self.Search_Bar_ENTRIES[f'to_{n}'].get()))
                elif search_type == '=':
                    searching[option].add(self.Search_Bar_ENTRIES[f'equal_{n}'].get())
                else:
                    searching[option].add((self.Search_Bar_ENTRIES[f'like_{n}'].get(),))

            for k,v in searching.items(): # OVO JE ZBOG SETOVA DA PREBACI U LISTU
                if len(v)==1:   # Uvek je prvo set jer pretpostavlja da ce ih biti vise istih
                    searching[k] = list(v)[0]
            return searching

        focus = self.buttons.NoteBook.index(self.buttons.NoteBook.select())
        if focus != 2: # Ovo je da bi SLIKE table mogao sa prazan search da filtrira sta se nalazi u PACIJENT tabeli
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

        if focus==0:
            self.PatientTable_IDs.clear()
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items(),self.Table_Pacijenti)
            searching = searching_dict_create()
            view = self.LoggingData(self.DB.execute_join_select("pacijenti",*(['id_pacijent']+columns),**searching),"Pacijenti Search SELECT")

            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)

        elif focus==1:
            columns = self.selected_columns(self.MKB_ColumnVars.items(),self.Table_MKB)
            searching = searching_dict_create()
            view = self.LoggingData(self.DB.execute_select("mkb10 2010",*(columns),**searching),"MKB Search SELECT")

            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_MKB)

        elif focus==2:
            columns = self.selected_columns(self.Slike_ColumnVars.items(),self.buttons.Table_Slike)
            searching = searching_dict_create()
            view = self.LoggingData(self.DB.execute_select("slike",*(['id_pacijent']+columns),**searching),"Slike Search SELECT")
  
            for item in self.buttons.Table_Slike.get_children():
                self.buttons.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view,self.PatientTable_IDs)

        elif focus==3:
            columns = self.selected_columns(self.Logs_ColumnVars.items(),self.Table_Logs)
            searching = searching_dict_create()
            view = self.LoggingData(self.DB.execute_select("logs",*(columns),**searching),"Logs Search SELECT")
 
            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Logs)

        elif focus==4:
            columns = self.selected_columns(self.Session_ColumnVars.items(),self.Table_Session)
            searching = searching_dict_create()
            view = self.LoggingData(self.DB.execute_select("session",*(columns),**searching),"Session Search SELECT")

            for item in self.Table_Session.get_children():
                self.Table_Session.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Session)

    #@method_efficency
    #@error_catcher
    def filter_data(self,columns):
        print("---"*66)
        where = {}
        self.PatientTable_IDs.clear()
        for k,v in self.buttons.FilterOptions.items():
            if k in columns:
                where[k]=v[1].get()
        

        view = self.LoggingData(self.DB.execute_filter_select(where),"FILTER SELECT")
        if self.DB.Admin is True:
            Messagebox.ok(parent=self.buttons.MessageBoxParent ,title="Pacijenti Filter SELECT", message=self.DB.LoggingQuery)

        for item in self.Table_Pacijenti.get_children():
            self.Table_Pacijenti.delete(item)
        if view and len(view)!=0:
            for i, row in enumerate(view):
                # FROM DB Date Formate TO Table Date Format
                formatted_row = [i+1] + [datetime.strptime(cell,"%Y-%m-%d").strftime("%d-%b-%y") if isinstance(cell, date) \
                                         else "" if str(cell)=="None" \
                                            else cell for cell in row[1:]]
                self.PatientTable_IDs.append(row[0])
                self.Table_Pacijenti.insert('', END, values=formatted_row)

    #@method_efficency
    #@error_catcher
    def fill_MKBForm(self,event):
        print("---"*66)
        try:
            row = self.Table_MKB.item(self.Table_MKB.focus())['values'][1:]
            headings = [column for column, var in self.MKB_ColumnVars.items() if var.get()==1][1:]
            for col,val in zip(headings,row):
                self.buttons.MKB_FormVariables[col].set(val)
        except IndexError:
            return
    

    def MKB_double_click(self, event):
        if event.state & 0x0004:  # Control key is pressed
            self.add_MKB_DgForm(event, 'Dg Sporedna')
        elif event.state & 0x0100:  # Command key is pressed (on Mac)
            self.add_MKB_DgForm(event, 'Dg Sporedna')
        else:
            self.add_MKB_DgForm(event, 'Dg Glavna')

    def add_MKB_DgForm(self, event, column):
        try:
            mkb = self.Table_MKB.item(self.Table_MKB.focus())['values'][1]
            dg_Widget = self.buttons.Patient_FormVariables['pacijenti dijagnoza'][column]
            dg_Value = self.buttons.get_widget_value(dg_Widget)
            if not dg_Value:
                self.buttons.set_widget_value(dg_Widget,mkb)
            else:
                self.buttons.set_widget_value(dg_Widget,f"{dg_Value} , {mkb}")
        except IndexError:
            return
    
    #@method_efficency
    #@error_catcher
    def fill_PatientForm(self,event):
        print("---"*66)
        self.buttons.Clear_Form()
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            self.buttons.PatientFocus_ID = self.PatientTable_IDs[self.Table_Pacijenti.item(self.Table_Pacijenti.focus())['values'][0]-1] 
            patient = self.DB.get_patient_data(self.buttons.PatientFocus_ID)
        except IndexError:
            return
        for col,val in patient.items():
            for table in self.buttons.Patient_FormVariables.keys():
                try:
                    widget = self.buttons.Patient_FormVariables[table][col]
                    break
                except KeyError:
                    continue
            else:
                continue
            if isinstance(val,str) and "," in val:
                val = val.split(",")
                fix = []
                for v in val:
                    fix.append(v.strip())
                val = " , ".join(fix) if col not in ["Asistenti","Gostujući Specijalizant"] else ",\n".join(fix)
            self.buttons.set_widget_value(widget,val)
        TEXT = f"{patient["Ime"]} {patient["Prezime"]} "
        try:
            # FROM DB Date Formate TO Patient print Date Format
            TEXT += f"({datetime.strptime(patient['Datum Prijema'],"%Y-%m-%d").strftime("%d-%b-%y")})"
        except KeyError:
            pass
        self.buttons.PatientInfo.config(text=TEXT)
        self.buttons.FormTitle[0].configure(bootstyle='success')
  
    #@method_efficency
    #@error_catcher
    def fill_LogsForm(self,event):
        print("---"*66)
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            time = self.Table_Logs.item(self.Table_Logs.focus())['values'][1]
            query = f'SELECT `Full Query`,`Full Error` from logs WHERE `ID Time` = "{time}"'
            FullQuery,FullError = self.DB.execute_selectquery(query)[0]
            self.buttons.set_widget_value(self.buttons.Logs_FormVariables['Full Query'],FullQuery)
            self.buttons.set_widget_value(self.buttons.Logs_FormVariables['Full Error'],FullError)
        except IndexError:
            return

    #@method_efficency
    #@error_catcher
    def tab_change(self,event):
        def filter_buttons_state(state):
            for txt,button in self.buttons.Buttons.items():
                if 'Filter' in txt:
                    button.configure(state=state)

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
            tab_swapping(self.TablePacijenti_Columns[1:],'normal')
        elif focus==1:
            tab_swapping(self.TableMKB_Columns[1:],'disabled')
        elif focus==2:
            self.buttons.Slike_HideTable.grid()
            tab_swapping(self.TableSlike_Columns[1:],'disabled')
        elif focus==3:
            tab_swapping(self.TableLogs_Columns[1:],'disabled')
        elif focus==4:
            tab_swapping(self.TableSession_Columns[1:],'disabled')
        else:
            self.Search_Bar.grid_remove()
        
