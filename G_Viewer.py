from A_Variables import *
from B_Decorators import method_efficency,spam_stopper,error_catcher
from C_GoogleDrive import GoogleDrive
from D_Media import Media
from E_SQLite import Database
from F_DBMS import DBMS,Buttons


class TitleFrame:
    def __init__(self,root) -> None: 

        img,img_posX,img_posY = title_ImgData
        self.title_txt = title_Txt
        
        self.title_img = Image.open(img)
    
        self.Title_Frame = Canvas(root, height=title_height)
        self.Title_Frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.Title_Frame.bind('<Configure>',lambda event , canvas=self.Title_Frame , img_txt = self.title_txt,
                            image=self.title_img , text_posX=1/img_posX, text_posY=1/img_posY:
                            self.adjust_title_window(event , canvas , img_txt , image , text_posX , text_posY))
        self.reconect_button = ctk.CTkButton(root, text="Reconect", width=form_butt_width,height=form_butt_height//2, corner_radius=12, font=font_label(),
                                 fg_color=ThemeColors['warning'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=self.reconecting)
        

    def reconecting(self):
        print("RECONECTING...")

    def remove_title_frame(self,event):
        self.Title_Frame.grid_forget()

    def adjust_title_window(self,event,canvas:Canvas,img_txt,image,text_posX,text_posY):
        new_width = event.width
        new_height = event.height
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        canvas.image = tk_image 
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=NW, image=tk_image)
        canvas.create_text(new_width//text_posX, new_height//text_posY, anchor='nw', text=img_txt, font=font_title, fill=ThemeColors[titleTxtColor])
        self.Title_Frame.create_window(new_width//1.06, 10, anchor='n', window=self.reconect_button)

class FormFrame:
    def __init__(self, root:Tk) -> None:
        self.form_true = BooleanVar()
        self.form_true.set(True)
        self.root = root
        
        self.DBMS = DBMS()
        self.BUTT = Buttons()
        self.DB = self.DBMS.DB
        FormFrame.DefaultForm_button_fun = [self.BUTT.Add_Patient,
                                            self.BUTT.Update_Patient,
                                            self.BUTT.Delete_Patient,
                                            self.BUTT.Clear_Form]
        FormFrame.AlternativeForm_button_fun = [self.BUTT.Add_Image,
                                                self.BUTT.Update_Image,
                                                self.BUTT.Delete_Image,
                                                self.BUTT.Fill_FromImage]

        self.valid_notblank = root.register(self.BUTT.validate_notblank)
        self.valid_dijagnoza = root.register(self.BUTT.validate_dijagnoza)
        self.valid_godiste = root.register(self.BUTT.validate_godiste)

            # PARENT FRAME for FORMS
        self.Form_Frame = Frame(root, bd=bd_main_frame, relief=RIDGE)
        self.Form_Frame.grid(row=1, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky="nsew")
        self.Form_Frame.grid_rowconfigure(1,weight=1)

        self.BUTT.FormTitle = (self.Form_TopLabel(form_name),labelColor)

            # DEFAULT FORM CREATE
        self.DefaultForm = Frame(self.Form_Frame)
        self.DefaultForm.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.FormPatient_Create(self.DefaultForm,default_form_entry, form_groups['Default'])
        self.FormPatient_Buttons(self.DefaultForm,[3],default_form_buttons,'default')
            # ALTERNATIVE FORM CREATE
        self.AlternativeForm = Frame(self.Form_Frame)
        self.AlternativeForm.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.AlternativeForm.grid_remove()
        self.FormPatient_Create(self.AlternativeForm,alternative_form_entry,form_groups['Alternative'],-8)
        self.FormPatient_Buttons(self.AlternativeForm,[3],alternative_form_buttons,'alternative')
 
    def label_ImageLoad(self,images_list):
        return_images = []
        for (img,width,height) in images_list:
            raw_img = Image.open(img)
            resize_img = raw_img.resize((width,height))
            return_images.append(ImageTk.PhotoImage(resize_img))
        return return_images

    def Form_TopLabel(self,formname):
        swap_img,swapfocus_img,hide_img,hidefocus_img = self.label_ImageLoad(IMAGES["Swap"]+IMAGES["Hide"])

        swap = tb.Label(self.Form_Frame, image=swap_img)
        swap.grid(row=0, column=0, sticky ="nw")
        swap.bind("<ButtonRelease-1>",self.swap_forms)
        swap.bind("<Enter>", lambda event,img=swapfocus_img: self.hover(event,img))
        swap.bind("<Leave>", lambda event,img=swap_img: self.hover(event,img))

        hide = tb.Label(self.Form_Frame, image=hide_img)
        hide.grid(row=0, column=3, sticky ="ne")
        hide.bind("<ButtonRelease-1>",self.remove_form_frame)
        hide.bind("<Enter>", lambda event,img=hidefocus_img: self.hover(event,img))
        hide.bind("<Leave>", lambda event,img=hide_img: self.hover(event,img))

        lbl = tb.Label(self.Form_Frame, anchor="center", bootstyle=labelColor, text=formname, font=font_groups)
        lbl.grid(row=0, column=1, columnspan=2, padx=title_padding[0], pady=title_padding[1], sticky="nswe")
        return lbl

    def Images_MiniTable_Create(self,frame:Frame):
        scroll_x = tb.Scrollbar(frame, orient=HORIZONTAL, bootstyle=f"{bootstyle_table}-round")
        scroll_y = tb.Scrollbar(frame, orient=VERTICAL, bootstyle=f"{bootstyle_table}-round")

        table = tb.ttk.Treeview(frame, columns=["ID", "Slika"], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set, show='tree')
        table.grid(row=0, column=0, pady=0, sticky="nsew")
        table.bind("<Double-1>",self.BUTT.Show_Image_FullScreen)

        def fill_Opis(event):
            opis = event.widget.item(event.widget.focus()) \
                    ['values'][1] \
                        .split('_')[2] \
                            .split('.')[0]
            self.BUTT.Patient_FormVariables['slike']['Opis'].set(opis)

        table.bind("<ButtonRelease-1>",fill_Opis)
        table.bind("<KeyRelease-Down>",fill_Opis)
        table.bind("<KeyRelease-Up>",fill_Opis)
        
        scroll_x.grid(row=1, column=0, sticky="ew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.config(command=table.xview)
        scroll_y.config(command=table.yview)

        # Sprečavanje automatskog prilagođavanja frejma
        frame.grid_rowconfigure(0, weight=1) 
        frame.grid_columnconfigure(0, weight=1)

        table.column("#0", width=0, stretch=False)
        table.column("ID", width=30, stretch=True)  # Podesite širinu kolone ID
        table.column("Slika", width=400, stretch=True)  # Podesite širinu kolone Slika

        frame.grid_propagate(False)

        return table

    def FormPatient_Create(self, parent:Frame, form_dict, group, pad_k=0):
        n=1
        group_names = []
        group_childs = []

        for k,v in group.items():
            if k!='start':
                group_names.append(k)
            if v:
                group_childs.append(v+group_childs[-1]) if group_childs else group_childs.append(v)

        for i, (txt, data) in enumerate(form_dict.items()):           
            if i in group_childs:
                lbl = tb.Label(parent, anchor="center", justify='center',
                                bootstyle=labelColor, text=group_names[n-1], font=font_groups)
                lbl.grid(row=i+n, column=0, columnspan=4,
                         padx=title_padding[0], pady=title_padding[1], sticky="nsew")
                n +=1

            if txt in self.DB.pacijenti:
                table = 'pacijenti'
            elif txt in self.DB.pacijenti_dijagnoza:
                table = 'pacijenti dijagnoza'
            elif txt in self.DB.operaciona_lista:
                table = 'operaciona lista'
            elif txt in self.DB.slike:
                table = 'slike'
            #wraplength = 100 if ' ' in data[0] else None
            lbl = tb.Label(parent, anchor="center", justify='center', bootstyle=labelColor, text=data[0], font=font_label())
            lbl.grid(row=i+n, column=0, columnspan=2,
                     padx=(form_padding_entry[0][0],form_padding_entry[0][1]+pad_k), pady=form_padding_entry[1], sticky="nswe")

            if data[1] in ['StringVar','Combobox','Validate']:
                self.BUTT.Patient_FormVariables[table][txt] = StringVar()
                if data[1]=='StringVar':
                    ent = tb.Entry(parent, textvariable=self.BUTT.Patient_FormVariables[table][txt], width=data[2], font=font_entry)
                elif data[1]=='Combobox':
                    ent = tb.Combobox(parent, values=data[3], textvariable=self.BUTT.Patient_FormVariables[table][txt], width=data[2],
                                      font=font_entry, validate="focus", validatecommand=(self.valid_notblank, '%P'), state="readonly")
                    self.BUTT.Validation_Widgets.append(ent)
                elif data[1] == 'Validate':
                    validcmd = self.valid_dijagnoza if 'Dg' in txt else self.valid_godiste if txt=='Godište' else self.valid_notblank
                    ent = tb.Entry(parent, width=data[2], textvariable=self.BUTT.Patient_FormVariables[table][txt], font=font_entry,
                                   validate="focus", validatecommand=(validcmd, '%P'))
                    self.BUTT.Validation_Widgets.append(ent)
            elif data[1] == 'Text':
                height = 3 if txt=="Dg Latinski" else 2
                ent = tb.Text(parent, width=data[2], height=height, font=font_entry)
                self.BUTT.Patient_FormVariables[table][txt] = ent
            elif data[1] == 'DateEntry':
                ent = widgets.DateEntry(parent, width=data[2], borderwidth=2, dateformat="%d-%b-%Y", firstweekday=0)
                ent.entry.delete(0, END)
                self.BUTT.Patient_FormVariables[table][txt] = ent
            elif data[1] == 'Info':
                ent = tb.Label(parent, anchor="center", justify='center', bootstyle=labelColor, text="", font=entry_font)
                ent.grid(row=i+n, column=0, columnspan=4,  padx=form_padding_entry[0], pady=form_padding_entry[1], sticky="nswe")
                self.BUTT.PatientInfo = ent
                ent = None
            elif data[1] == 'Slike':
                ent = Frame(parent)
                ent.grid(row=i+n, column=0, columnspan=4,  padx=(12,0), pady=form_padding_entry[1], sticky="nswe")
                parent.grid_rowconfigure(i+n, weight=1)
                sliketable = self.Images_MiniTable_Create(ent)
                self.BUTT.Patient_FormVariables['slike'][txt] = sliketable
                ent = None
            if ent:
                ent.grid(row=i+n, column=2, columnspan=2, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky="w")

    def FormPatient_Buttons(self,parent,split,buttons,form):
        buttons_cmd = FormFrame.DefaultForm_button_fun if form=='default' else FormFrame.AlternativeForm_button_fun if form=='alternative' else None
        Frame(parent).grid(row=16, columnspan=4, pady=12) ## prazan frame za odvajanje (6*2 == 12)
        for i,((but,btype),cmd) in enumerate(zip(buttons,buttons_cmd)):
            if i in split or i==0:
                Buttons_Frame = Frame(parent)
                Buttons_Frame.grid(row=18+i, columnspan=4)
                Buttons_Frame.bind("<Enter>",self.BUTT.Validation_Method)

            butt = ctk.CTkButton(Buttons_Frame, text=but, width=form_butt_width,height=form_butt_height, corner_radius=12, font=font_label(),
                                 fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=cmd)
            butt.grid(row=0, column=i, padx=form_padding_button[0], pady=form_padding_button[1])
            self.BUTT.Buttons[but] = butt
            if btype:
                butt.configure(fg_color=ThemeColors[btype])
        Frame(parent).grid(row=24, columnspan=4, pady=12) ## prazan frame za odvajanje (6*2 == 12)    

    def remove_form_frame(self,event):
        self.Form_Frame.grid_forget()
        self.form_true.set(False)
    
    def swap_forms(self,event):
        if self.DefaultForm.winfo_ismapped():
            self.DefaultForm.grid_remove()
            self.AlternativeForm.grid()
        elif self.AlternativeForm.winfo_ismapped():
            self.AlternativeForm.grid_remove()
            self.DefaultForm.grid()

    def hover(self,event,img):
        event.widget.config(image=img)

class WindowFrame:
    def __init__(self, root:Tk,) -> None:
        self.DBMS = DBMS()
        self.BUTT = Buttons()
        self.BUTT.FilterOptions = {"Datum Operacije":"Operisan" , "Datum Otpusta":"Otpušten"}
        WindowFrame.MKB_buttons = [self.BUTT.Add_MKB,
                                   self.BUTT.Update_MKB,
                                   self.BUTT.Delete_MKB,
                                   self.BUTT.import_many_MKB]

        # PARENT FRAME for RIGHT PANEL
        notebookROW = 9
        Window_Frame = Frame(root)
        Window_Frame.grid(row=1, column=1, padx=shape_padding[0], pady=shape_padding[1], sticky="nsew")
        self.BUTT.MessageBoxParent = Window_Frame
                # Ovo znaci da ce se NOTEBOOK siriti sa WINDOW
        Window_Frame.grid_rowconfigure(notebookROW, weight=1) 
        Window_Frame.grid_columnconfigure(0, weight=1)

            # Search BAR Frame -- TOP of RIGHT PANES
        searchButtonROW = 8
        self.DBMS.Search_Bar = Frame(Window_Frame, bd=bd_inner_frame, relief=RIDGE)
        self.DBMS.Search_Bar.grid(row=0, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky="nsew")
                # Ovo znaci da ce se zadnja 2 BUTONNA uvek biti desno
        self.DBMS.Search_Bar.grid_columnconfigure(searchButtonROW,weight=1)
        self.DBMS.Search_Bar.grid_rowconfigure(0,weight=1)     
                # Create SEARCH BAR
        self.SearchBar_StaticPart(searchButtonROW)
        self.Search_Add,self.Search_Remove = self.SearchBar_AddRemove()

        self.SearchBar_DynamicPart()
        for _ in range(max_searchby-1):
            self.search_bar_add()
        for _ in range(max_searchby-1):
            self.search_bar_remove()
        

            # NOTE NOTEBOOK
        self.BUTT.NoteBook = tb.Notebook(Window_Frame)#, bootstyle=bootstyle_table)
        self.BUTT.NoteBook.grid(row=notebookROW, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky="nsew")
        self.BUTT.NoteBook.bind("<<NotebookTabChanged>>", self.DBMS.tab_change)

                # NOTEBOOK Tab PACIJENTI
        self.DBMS.Table_Pacijenti = self.NotebookTab_Create("Pacijenti",table=True,
                                extra=(self.Checkbutton_Create,{'row':0,'column':0,'rowspan':1,'columnspan':2}))
        self.DBMS.Table_Pacijenti.bind("<ButtonRelease-1>",self.DBMS.fill_PatientForm)
        self.DBMS.Table_Pacijenti.bind("<KeyRelease-Down>",self.DBMS.fill_PatientForm)
        self.DBMS.Table_Pacijenti.bind("<KeyRelease-Up>",self.DBMS.fill_PatientForm)
        self.DBMS.selected_columns(self.DBMS.Pacijenti_ColumnVars.items(),self.DBMS.Table_Pacijenti)

                # NOTEBOOK Tab MKB Sifarnik
        self.DBMS.Table_MKB = self.NotebookTab_Create("MKB10 2010",table=True,
                                extra=(self.MKB_Entry_Create,{'row':5,'column':0,'rowspan':1,'columnspan':2}))
        self.DBMS.Table_MKB.bind("<ButtonRelease-1>",self.DBMS.fill_MKBForm)
        self.DBMS.Table_MKB.bind("<KeyRelease-Down>",self.DBMS.fill_MKBForm)
        self.DBMS.Table_MKB.bind("<KeyRelease-Up>",self.DBMS.fill_MKBForm)
        self.DBMS.Table_MKB.bind("<Double-1>",self.DBMS.MKB_double_click)
        for val in self.DBMS.MKB_ColumnVars.values():
            val.set(1)
        self.DBMS.selected_columns(self.DBMS.MKB_ColumnVars.items(),self.DBMS.Table_MKB)

                
        self.BUTT.Table_Slike = self.NotebookTab_Create("Slike",table=F_SIZE*50, expand=(1,5),
                                extra=(self.Slike_SideFrame,{'row':1,'column':5,'rowspan':2,'columnspan':1}))
        self.BUTT.Table_Slike.bind("<ButtonRelease-1>", self.BUTT.Show_Image)
        self.BUTT.Table_Slike.bind("<KeyRelease-Down>", self.BUTT.Show_Image)
        self.BUTT.Table_Slike.bind("<KeyRelease-Up>", self.BUTT.Show_Image)
        for val in self.DBMS.Slike_ColumnVars.values():
            val.set(1)
        self.DBMS.selected_columns(self.DBMS.Slike_ColumnVars.items(),self.BUTT.Table_Slike)

            # NOTEBOOK Tab LOGS
        self.DBMS.Table_Logs = self.NotebookTab_Create("Logs", table=True, expand=(1,5),
                                extra=(self.Log_SideFrame,{'row':1,'column':5,'rowspan':2,'columnspan':1}))
        self.DBMS.Table_Logs.bind("<ButtonRelease-1>",self.DBMS.fill_LogsForm)
        self.DBMS.Table_Logs.bind("<KeyRelease-Down>",self.DBMS.fill_LogsForm)
        self.DBMS.Table_Logs.bind("<KeyRelease-Up>",self.DBMS.fill_LogsForm)
        for val in self.DBMS.Logs_ColumnVars.values():
            val.set(1)
        self.DBMS.selected_columns(self.DBMS.Logs_ColumnVars.items(),self.DBMS.Table_Logs)
        #self.BUTT.NoteBook.hide(3)

            # NOTEBOOK Tab SESSION
        self.DBMS.Table_Session = self.NotebookTab_Create("Session", table=True)
        for val in self.DBMS.Session_ColumnVars.values():
            val.set(1)
        self.DBMS.selected_columns(self.DBMS.Session_ColumnVars.items(),self.DBMS.Table_Session)
        
            # SETTINGS TAB
        self.DBMS.Settings_Tab = self.NotebookTab_Create("Settings")

    def SearchBar_StaticPart(self,searchButtonROW):
            # JUST LABEL for SEARCH (SEARCH BY, PRETRAZI)
        tb.Label(self.DBMS.Search_Bar, anchor='center', bootstyle=labelColor, text="SEARCH BY", font=font_entry).grid(
                            row=0, column=1, rowspan=max_searchby, padx=form_padding_button[0], pady=form_padding_button[1], sticky="nsew")
            # FILTER OPTIONS
        filterFrame = Frame(self.DBMS.Search_Bar)
        filterFrame.grid(row=0,column=searchButtonROW,rowspan=max_searchby,sticky="se")
        self.Roundbutton_Create(filterFrame)    
        butf = ctk.CTkButton(filterFrame, text="FILTER\nBOTH", width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                            command=lambda column=["Datum Operacije","Datum Otpusta"]: self.DBMS.filter_data(column))
        butf.grid(row=0, column=2, rowspan=max_searchby,
                padx=(form_padding_button[0][0],33), pady=form_padding_button[1], sticky='se')
        self.BUTT.Buttons['Filter Both'] = butf

            # BUTTONS for SEARCH and SHOWALL
        buts = ctk.CTkButton(self.DBMS.Search_Bar, text="SEARCH", width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'],  text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.search_data)
        buts.grid(row=0, column=searchButtonROW+3, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky='se')
        self.BUTT.Buttons['Search'] = buts

        buta = ctk.CTkButton(self.DBMS.Search_Bar, text="SHOW ALL", width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.showall_data)
        buta.grid(row=0, column=searchButtonROW+4, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky='se')
        self.BUTT.Buttons['Show All'] = buta

    def SearchBar_AddRemove(self):
                # BUTTONS for adding and removing SEARCH CRITERIA
        add = ctk.CTkButton(self.DBMS.Search_Bar, text=" + ", width=20, height=20, corner_radius=10,
                                        fg_color=ThemeColors['success'], text_color=ThemeColors['dark'], font=font_label(), command=self.search_bar_add)
        add.grid(row=0, rowspan=max_searchby, column=0, padx=form_padding_button[0], pady=form_padding_button[1], sticky='n')

        remove = ctk.CTkButton(self.DBMS.Search_Bar, text=" - ", width=20, height=20, corner_radius=10,
                                           fg_color=ThemeColors['danger'], text_color=ThemeColors['dark'], font=font_label(), command=self.search_bar_remove)
        remove.grid(row=0, rowspan=max_searchby, column=0, padx=form_padding_button[0], pady=form_padding_button[1], sticky='s')
        remove.grid_remove()

        return add,remove

    def SearchBar_DynamicPart(self):
        n = self.DBMS.Search_Bar_ON
        ROW = self.DBMS.Search_Bar_ON-1

        def grid_set(widget,col,colspan=1,remove=True):
            widget.grid(row=ROW, column=col, columnspan=colspan, padx=search_padding[0], pady=search_padding[1],sticky='ew')
            if remove:
                widget.grid_remove()

        col_val = self.DBMS.TablePacijenti_Columns[1:] 
        Search_option = tb.Combobox(self.DBMS.Search_Bar, width=19, values=col_val, height=len(col_val), font=font_entry, state="readonly")
        self.DBMS.Search_Bar_ENTRIES[f'search_option_{self.DBMS.Search_Bar_ON}'] = Search_option
        grid_set(Search_option,4,remove=False)
        Search_option.bind("<<ComboboxSelected>>", lambda event: self.DBMS.Options(n,event))

        Search_type_label = tb.Label(self.DBMS.Search_Bar, width=7, anchor='center', bootstyle=labelColor, text="", font=font_entry)
        self.DBMS.Search_Bar_ENTRIES[f'search_type_{self.DBMS.Search_Bar_ON}'] = Search_type_label
        grid_set(Search_type_label,5)
    
        sex_val = ['Muško','Žensko']
        Search_input_equal = tb.Combobox(self.DBMS.Search_Bar, values=sex_val, height=len(sex_val), width=search_1_width, font=font_entry, state="readonly")
        self.DBMS.Search_Bar_ENTRIES[f'equal_{self.DBMS.Search_Bar_ON}'] = Search_input_equal
        grid_set(Search_input_equal,6,colspan=2)

        Search_input_like = tb.Entry(self.DBMS.Search_Bar, width=search_1_width, font=font_entry)
        self.DBMS.Search_Bar_ENTRIES[f'like_{self.DBMS.Search_Bar_ON}'] = Search_input_like
        grid_set(Search_input_like,6,colspan=2)

        Search_date_from = widgets.DateEntry(self.DBMS.Search_Bar, width=search_2_width+2, dateformat="%d-%b-%Y", firstweekday=0)
        Search_date_from.entry.delete(0,END)
        self.DBMS.Search_Bar_ENTRIES[f'date_from_{self.DBMS.Search_Bar_ON}'] = Search_date_from
        grid_set(Search_date_from,6)

        Search_date_to = widgets.DateEntry(self.DBMS.Search_Bar, width=search_2_width+2, dateformat="%d-%b-%Y", firstweekday=0)
        Search_date_to.entry.delete(0,END)
        self.DBMS.Search_Bar_ENTRIES[f'date_to_{self.DBMS.Search_Bar_ON}'] = Search_date_to
        grid_set(Search_date_to,7)

        Search_input_from = tb.Entry(self.DBMS.Search_Bar, width=search_2_width, font=font_entry)
        self.DBMS.Search_Bar_ENTRIES[f'from_{self.DBMS.Search_Bar_ON}'] = Search_input_from
        grid_set(Search_input_from,6)

        Search_input_to = tb.Entry(self.DBMS.Search_Bar, width=search_2_width, font=font_entry)
        self.DBMS.Search_Bar_ENTRIES[f'to_{self.DBMS.Search_Bar_ON}'] = Search_input_to
        grid_set(Search_input_to,7)

    def search_bar_remove(self):
        to_remove = [k for k in self.DBMS.Search_Bar_ENTRIES.keys() if int(k[-1]) == self.DBMS.Search_Bar_ON]
        for key in to_remove:
            self.BUTT.empty_widget(self.DBMS.Search_Bar_ENTRIES[key])
            self.DBMS.Search_Bar_ENTRIES[key].grid_remove()
        self.DBMS.Search_Bar_ON-=1

        if not self.Search_Add.winfo_ismapped():
            self.Search_Add.grid()
        if self.DBMS.Search_Bar_ON==1:
            self.Search_Remove.grid_remove()

    def search_bar_add(self):
        if not self.Search_Remove.winfo_ismapped():
            self.Search_Remove.grid()
        self.DBMS.Search_Bar_ON+=1
        try:
            self.DBMS.Search_Bar_ENTRIES[f'search_option_{self.DBMS.Search_Bar_ON}'].grid()
        except KeyError:
            self.SearchBar_DynamicPart()

        if self.DBMS.Search_Bar_ON==max_searchby:
            self.Search_Add.grid_remove()

    def NotebookTab_Create(self,txt,table=False,extra=False,expand=(1,0)):
        notebook_frame = tb.Frame(self.BUTT.NoteBook)
        self.BUTT.NoteBook.add(notebook_frame, text=txt)
        if extra:
            extra_frame = Frame(notebook_frame)
            extra_frame.grid(row=extra[1]['row'], rowspan=extra[1]['rowspan'],
                             column=extra[1]['column'], columnspan=extra[1]['columnspan'], sticky="nswe")
            extra[0](extra_frame)
        if table:
            if str(table).isdigit():
                parent_frame = Frame(notebook_frame, width=table)
                parent_frame.grid(row=1,rowspan=2,column=0, columnspan=2, pady=0, sticky="nsew")
                parent_frame.grid_propagate(False)
                parent_frame.grid_rowconfigure(1, weight=1)
                parent_frame.grid_columnconfigure(0, weight=1)
                if txt=='Slike':
                    self.BUTT.Slike_HideTable = parent_frame
            else:
                parent_frame = notebook_frame
            scroll_x = tb.Scrollbar(parent_frame, orient=HORIZONTAL, bootstyle=f"{bootstyle_table}-round")
            scroll_y = tb.Scrollbar(parent_frame, orient=VERTICAL, bootstyle=f"{bootstyle_table}-round")

            table = tb.ttk.Treeview(parent_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, pady=0, sticky="nsew")
            
            scroll_x.grid(row=2, column=0, sticky="ew")
            scroll_y.grid(row=1, column=1, sticky="ns")
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            notebook_frame.grid_rowconfigure(expand[0], weight=1)
            notebook_frame.grid_columnconfigure(expand[1], weight=1)

        return table if table else notebook_frame

    def MKB_Entry_Create(self,parent_frame):
        parent_frame.grid_columnconfigure(1,weight=1)
        for i,(column,values) in enumerate(MKB_Entry.items()):
            if column=="Buttons":
                frame = Frame(parent_frame,bd=4,relief=RIDGE)
                frame.grid(row=0, column=i, sticky="nsew")
                frame.grid_rowconfigure(0,weight=1)
                for j,(butt,btype) in enumerate(values):
                    button = ctk.CTkButton(frame, text=butt, width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=WindowFrame.MKB_buttons[j])
                    button.grid(row=0, column=j,padx=form_padding_button[0], pady=form_padding_button[1], sticky='nse')
                    self.BUTT.Buttons[butt] = button
                    if btype:
                        button.configure(fg_color=ThemeColors[btype], text_color=ThemeColors[dangerButtTxtColor])
            else:
                self.BUTT.MKB_FormVariables[column] = StringVar()
                frame = Frame(parent_frame,bd=4,relief=RIDGE)
                frame.grid(row=0, column=i, sticky="nsew")
                tb.Label(frame, anchor='center', justify='center', bootstyle=labelColor, text=values[0], font=font_entry).grid(
                            row=0, column=0, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky="nsew")
                tb.Entry(frame, textvariable=self.BUTT.MKB_FormVariables[column], width=values[1], font=font_entry).grid(
                    row=0, column=1, columnspan=2, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky="ew")
                frame.grid_rowconfigure(0,weight=1)
                frame.grid_columnconfigure(1,weight=1)

    def Slike_SideFrame(self,parent_frame:Frame):
        Media.Slike_Viewer = Canvas(parent_frame)
        Media.Slike_Viewer.pack(side=LEFT, fill=BOTH, expand=True)

        self.scroll_y = tb.Scrollbar(Media.Slike_Viewer, orient=VERTICAL, command=Media.Slike_Viewer.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.scroll_x = tb.Scrollbar(Media.Slike_Viewer, orient=HORIZONTAL, command=Media.Slike_Viewer.xview)
        self.scroll_x.pack(side=BOTTOM, fill=X)
        Media.Slike_Viewer.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)


    def Log_SideFrame(self,parent_frame):
        lbl1 = tb.Label(parent_frame,text="Full Query", anchor="center", justify='center', bootstyle=labelColor, font=font_label())
        lbl1.grid(row=0, column=0)
        text1 = tb.Text(parent_frame, width=form_large_width, font=font_entry)
        text1.grid(row=1, column=0, sticky='nsew')
        self.BUTT.Logs_FormVariables['Full Query'] = text1
        lbl1 = tb.Label(parent_frame,text="Full Error", anchor="center", justify='center', bootstyle=labelColor, font=font_label())
        lbl1.grid(row=2, column=0)
        text2 = tb.Text(parent_frame, width=form_large_width, font=font_entry)
        text2.grid(row=3, column=0, sticky='nsew')
        self.BUTT.Logs_FormVariables['Full Error'] = text2

        parent_frame.grid_rowconfigure([1,3],weight=1)

        #Media.Slike_Viewer.configure(bd=5, relief='solid', highlightthickness=2, highlightbackground='black')

        parent_frame.grid_columnconfigure(0,weight=1)
        parent_frame.grid_rowconfigure(1,weight=1)     

    def Checkbutton_Create(self,parent_frame):
        table = self.DBMS.TablePacijenti_Columns
        groups = [table.index("Starost"),table.index("Dg Glavna"),table.index("Datum Prijema"),table.index("Operator")]
        labels = ["Pacijent","Dijagnoza","Datum","Doktori"]
        for i,column in enumerate(table):
            if i in groups:
                check_pos = i
                group_pos = groups.index(i)
                try:
                    groupnum = (groups[group_pos+1]-i)
                except IndexError:
                    groupnum = len(table)-i
                frame = Frame(parent_frame,bd=4,relief=RIDGE)
                frame.grid(row=0,column=group_pos, sticky="w")
                frame.columnconfigure([i for i in range(groupnum)],weight=1)

                lbl = tb.Label(frame,anchor="center", bootstyle=labelColor, text=labels[group_pos], font=font_label())
                lbl.grid(row=0, column=0, columnspan=groupnum, pady=(0,6))
            if i>=groups[0]:
                txt = column if " " not in column else column.split()[1]
                tb.Checkbutton(frame, text=txt, variable=self.DBMS.Pacijenti_ColumnVars[column],
                                bootstyle=bootstyle_check).grid(row=1, column=i-check_pos, padx=6)
            self.DBMS.Pacijenti_ColumnVars[column].set(1)
        parent_frame.columnconfigure(len(labels),weight=1)

    def Roundbutton_Create(self,parent_frame):
        for i,(col,txt) in enumerate(self.BUTT.FilterOptions.items()):
            self.BUTT.FilterOptions[col] = [txt,IntVar()] # Ovde dodajen varijablu int da bi mogao da menjam sa json

            cb = tb.Checkbutton(parent_frame, text=txt, variable=self.BUTT.FilterOptions[col][1], bootstyle="success, round-toggle")
            cb.grid(row=0, column=i, padx=form_padding_button[0], pady=(0,3))

            butt = ctk.CTkButton(parent_frame, text="FILTER", width=form_butt_width, height=form_butt_height//2, corner_radius=10,
                            font=font_label(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'],text_color_disabled=ThemeColors['secondary'],
                                command=lambda column=col: self.DBMS.filter_data(column))
            butt.grid(row=1, column=i, padx=form_padding_button[0], pady=(0,3))
            self.BUTT.Buttons[f"Filter {txt}"] = butt

class GUI:
    def GoogleDrive_Decorating(self):
        for name, method in inspect.getmembers(GoogleDrive, predicate=inspect.isfunction):
            print(f"Decorating {name}")
            decorated_method = method_efficency(self.GD.UserSession)(
                error_catcher(self.DB)(method)
                )
            setattr(self.GD, name, decorated_method.__get__(self.GD, type(self.GD)))

    def Media_Decorating(self):
        for name, method in inspect.getmembers(Media, predicate=inspect.isfunction):
            if name not in ['move_from','move_to']:
                print(f"Efficency {name}")
                decorated_method = method_efficency(self.GD.UserSession)(
                    error_catcher(self.DB)(method)
                    )
                setattr(Media, name, decorated_method)

    def Database_Decorating(self):
        for name, method in inspect.getmembers(Database, predicate=inspect.isfunction):
            if "execute" in name or "get" in name:
                print(f"Efficency {name}")
                decorated_method = method_efficency(self.GD.UserSession)(
                    error_catcher(self.DB)(method)
                    ) 
                setattr(self.DB, name, decorated_method.__get__(self.DB, type(self.DB)))
            else:
                print(f"Error {name}")
                decorated_method = error_catcher(self.DB)(method)
                setattr(self.DB, name, decorated_method.__get__(self.DB, type(self.DB)))

    
    def Buttons_Decorating(self):
        for name, method in inspect.getmembers(Buttons, predicate=inspect.isfunction):
            for i in ["Add","Update","Delete","Show_Image","Fill"]:
                if i in name:
                    print(f"Efficency {name}")
                    decorated_method = method_efficency(self.GD.UserSession)(
                    error_catcher(self.DB)(method)
                    )
                    setattr(self.BUTT, name, decorated_method.__get__(self.BUTT, type(self.BUTT)))
                    break
            else:
                print(f"Error {name}")
                decorated_method = error_catcher(self.DB)(method)
                setattr(self.BUTT, name, decorated_method.__get__(self.BUTT, type(self.BUTT)))

    def DBMS_Decorating(self):
        for name, method in inspect.getmembers(DBMS, predicate=inspect.isfunction):
            for i in ["data","tab","Form"]:
                if i in name:
                    print(f"Efficency {name}")
                    decorated_method = method_efficency(self.GD.UserSession)(
                        error_catcher(self.DB)(method)
                    )
                    setattr(self.DBMS, name, decorated_method.__get__(self.DBMS, type(self.DBMS)))
                    break
            else:
                print(f"Error {name}")
                decorated_method = error_catcher(self.DB)(method)
                setattr(self.DBMS, name, decorated_method.__get__(self.DBMS, type(self.DBMS)))

    def Buttons_SpamStopper(self):
        for button in self.BUTT.Buttons.values():
            last_cmd = button.cget('command')
            button.configure(command=spam_stopper(button,self.root)(last_cmd))

    def EXIT(self):
        response = Messagebox.show_question("Do you want to save the changes before exiting?", "Close", buttons=["Exit:secondary","Save:success"])
        if response == "Save":
            threading.Thread(target=self.uploading_to_GoogleDrive).start()
            self.root.destroy()
        if response == "Exit":
            self.root.destroy()
    
    def uploading_to_GoogleDrive(self):
        print("Uploading to Google Drive...")
        #self.GD.upload_UpdateFile(RHMH_DB['id'],"RHMH.db",RHMH_DB['mime'])
        print("Upload finished")

    def show_form_frame(self):
        if not self.Form.Form_Frame.winfo_ismapped():
            self.Form.Form_Frame.grid(row=1, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky="nsew")
            self.Form.form_true.set(True)
        else:
            self.Form.Form_Frame.grid_forget()
            self.Form.form_true.set(False) 

    def show_title_frame(self):
        if not self.Title.Title_Frame.winfo_ismapped():
            self.Title.Title_Frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
            self.title_true.set(True)
        else:
            self.Title.Title_Frame.grid_forget()
            self.title_true.set(False) 

    def RootMenu_Create(self):
        def do_popup(event): 
            try: 
                m.tk_popup(event.x_root, event.y_root) 
            finally: 
                m.grab_release() 
        m = Menu(self.root, tearoff = 0) 
        self.title_true = BooleanVar()
        self.title_true.set(True)
        m.add_checkbutton(label="Show Title", variable=self.title_true, command=self.show_title_frame)
        m.add_checkbutton(label="Show Form", variable=self.Form.form_true, command=self.show_form_frame)
        m.add_separator() 
        m.add_command(label ="Copy") 
        m.add_command(label ="Paste") 
        m.add_command(label ="Reload")
        m.add_command(label ="Rename")
        self.root.bind("<Button-3>", do_popup)
        return m
    
    def lose_focus(self,event):
        event.widget.focus()

    def __init__(self, root:Tk):
        self.GD = GoogleDrive()
        self.GD.download_File(RHMH_DB['id'],"RHMH.db")
        self.DBMS = DBMS()
        self.BUTT = self.DBMS.buttons
        self.BUTT.ROOT = root
        self.DB = self.DBMS.DB

        # DECORATING
        self.GoogleDrive_Decorating()
        self.Media_Decorating()
        self.Database_Decorating()
        self.Buttons_Decorating()
        self.DBMS_Decorating()
        
        self.root = root
        self.root.title(app_name)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.iconbitmap("C:/Users/vurun/Desktop/App/Slytherin-Emblem_icon.ico")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.Title = TitleFrame(self.root)
        self.Form = FormFrame(self.root)
        self.Window = WindowFrame(self.root)
        
        self.root.bind("\u004D\u0055\u0056",lambda event,root=self.root,notebook=self.DBMS.buttons.NoteBook: 
                                                    self.DBMS.DB.GodMode_Password(event,root,notebook))
        self.root.protocol("WM_DELETE_WINDOW",self.EXIT)
        self.Buttons_SpamStopper()
        self.menu = self.RootMenu_Create()
        self.root.bind("<Button-1>",self.lose_focus)
    
root = Tk()

style = tb.Style(theme=THEME)

# CUVA u dicty BOJE iz TEME
for color_label in Colors.label_iter():
    color = style.colors.get(color_label)
    ThemeColors[color_label] = color
print(ThemeColors)
ThemeColors_Dict = ThemeColors

# MENJA boju na TABOVIMA od NOTEBOOK-a
style.configure("TNotebook.Tab")
style.map("TNotebook.Tab", background=[("selected", ThemeColors['selectbg']),
                                       ("!selected", ThemeColors['active'])])
style.map("TNotebook.Tab", foreground=[("selected", ThemeColors['selectfg']),
                                       ("!selected", ThemeColors[theme_fg])])

style.configure("Treeview", rowheight=int(F_SIZE*2.2))
style.map("Treeview.Heading", background=[('active',ThemeColors["primary"])])
style.configure("Treeview.Heading",font=font_label('normal'), padding=(0,F_SIZE//2))

# Menja samo FONT SIZE za TABLE i DATAENTRY
default_font = nametofont("TkDefaultFont")
entry_font = nametofont('TkTextFont')
default_font.configure(size=def_font[1])
entry_font.configure(size=def_font[1])

GUI = error_catcher()(GUI)
TitleFrame = error_catcher()(TitleFrame)
FormFrame = error_catcher()(FormFrame)
WindowFrame = error_catcher()(WindowFrame)
DBMS = error_catcher()(DBMS)
Buttons = error_catcher()(Buttons)
Database = error_catcher()(Database)
GoogleDrive = error_catcher()(GoogleDrive)

app = GUI(root)
root.mainloop()