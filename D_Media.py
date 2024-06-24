from A_Variables import *
pillow_heif.register_heif_opener()

class Media:
    ReaderSetting = easyocr.Reader(['rs_latin','en'])
    @staticmethod
    def is_date(date_string):
        try:
            date_string = date_string.replace(" ","")
            date_string = date_string if date_string[-1].isdigit() else date_string[:-1]
            date = datetime.strptime(str(date_string), '%d.%m.%Y').strftime("%d-%b-%y")
            return date
        except ValueError:
            return False
        
    @staticmethod
    def mkb_find(detection,nextline):
        try:
            mkb = detection.split()[3]
            return mkb,False
        except IndexError:
            mkb = nextline.split()[0]
            return mkb,True

    @staticmethod
    def mkb_fix(mkb):
        if mkb[0].isdigit():
            fix='X'
            if mkb[0] in ['5','8']:
                fix = 'S'
            elif mkb[0]=='2':
                fix = 'Z'
            elif mkb[0]=='0':
                fix = 'D'
            mkb = fix + mkb[1:]
        mkb = mkb[0]+mkb[1:].replace("O","0")
        mkb.replace('?','1')
        mkb = mkb.replace(",","")
        mkb = mkb.replace(".","")
        if len(mkb)==4:
            mkb = mkb[:3]+"."+mkb[-1]
        return mkb

    @staticmethod
    def Image_Reader(img_blob):
        image = np.array(Image.open(io.BytesIO(img_blob)))
        result = Media.ReaderSetting.readtext(image, detail=0, mag_ratio=1.15)

        def extend_variable(i, variable, searchlist, image_text):
            j = i + 1
            while j < len(image_text) and not any((image_text[j]).startswith(prefix) for prefix in searchlist):
                variable += (" " + image_text[j])
                j += 1
            return variable

        # Initialize variables
        OUTPUT = {  "Datum Operacije": None,
                    "Dg Glavna": list(),
                    "Dg Sporedna": list(),
                    "Dg Latinski": None,
                    "Operator": list(),
                    "Asistenti": list(),
                    "Anesteziolog": list(),
                    "Anestetičar": list(),
                    "Instrumentarka": list(),
                    "Gostujući Specijalizant":list()   }
        DoctorsImage_dict = {"Operator":("Operator",["Operator"]),
                             "Asist":("Asistenti",["Asistent 1","Asistent 2","Asistent 3","Asistent"]),
                            "Anestezio":("Anesteziolog",["Anesteziolog"]),
                            "Anestet":("Anestetičar",["Anestetičar","Anesteticar"]),
                            "Instru":("Instrumentarka",["Instrumentarka","Instrumentar"]),
                            "Gostuju": ("Gostujući Specijalizant",["Gostujući specijalizant","Gostujuci specijalizant"])}
        prosao_datum = False

        for i, detection in enumerate(result):
            if prosao_datum is False and detection in ['PACIJENT','OPERACIONA LISTA','godište']:
                prosao_datum = True
            if  prosao_datum is False or not OUTPUT["Datum Operacije"]:
                date = Media.is_date(detection)
                if date:
                    OUTPUT['Datum Operacije'] = date
                    prosao_datum = True
            if "Glavna operativna dijagnoza" in detection:
                mkb,nextline = Media.mkb_find(detection,result[i+1])
                if nextline is False:
                    MKB = Media.mkb_fix(mkb)
                else:
                    MKB = Media.mkb_fix("L"+mkb)
                OUTPUT['Dg Glavna'].append(MKB)
                if not OUTPUT['Dg Latinski']:
                    try:
                        if nextline is False:
                            Dg_Latinski = detection.split(mkb)[1].strip()
                        else:
                            Dg_Latinski = result[i+1].split(mkb)[1].strip()
                        Dg_Latinski = extend_variable(i, Dg_Latinski, ["Glavn", "Spored", "Operac"], result)
                        OUTPUT['Dg Latinski'] = Dg_Latinski.replace("|","l")
                    except IndexError:
                        continue

            elif "Sporedna operativna dijagnoza" in detection:
                mkb,nextline = Media.mkb_find(detection,result[i+1])
                if nextline is False:
                    MKB = Media.mkb_fix(mkb)
                else:
                    MKB = Media.mkb_fix("L"+mkb)
                OUTPUT['Dg Sporedna'].append(MKB)
                
            else: # DOCTORS
                for prefix,(doctorType,fixlist) in DoctorsImage_dict.items():
                    if detection.capitalize().startswith(prefix):
                        doctors: str
                        doctors = extend_variable(i, detection, list(DoctorsImage_dict.keys())+["Preme","Anest"], result)
                        for fix in fixlist+['-','_',',','.',':',';']:
                            doctors = doctors.replace(fix,"")
                        doctors = doctors.replace('ll',"Il")
                        doctors = " ".join(doctors.split())
                        if prefix == 'Gostuju':
                            DOCTORS = []
                            doctors = doctors.split()
                            for i,doc in enumerate(doctors):
                                if doc in ['Dr','dr']:
                                    DOCTORS.append(" ".join(doctors[i:i+3]))
                            OUTPUT[doctorType] += DOCTORS
                        else:
                            if doctors:
                                if doctorType == "Asistenti":
                                    OUTPUT[doctorType].append(doctors)
                                elif not OUTPUT[doctorType]:
                                    OUTPUT[doctorType] = [doctors]
        return OUTPUT

    @staticmethod
    def get_image(image_blob_data): # Format za Canvas
        image = Image.open(io.BytesIO(image_blob_data))
        return image

    @staticmethod
    def resize_image(image, max_width, max_height):
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        scale_ratio = min(width_ratio, height_ratio)

        new_width = int(image.width * scale_ratio)
        new_height = int(image.height * scale_ratio)
        return image.resize((new_width, new_height), Image.LANCZOS), new_width, new_height

    @staticmethod
    def create_video_thumbnail(video_data):
        if not os.path.exists('temporary'):
            os.makedirs('temporary')
        video_file = 'temporary/temp_video.mp4'
        with open(video_file, 'wb') as f:
            f.write(video_data)

        # Capture the first frame of the video
        cap = cv2.VideoCapture(video_file)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("Failed to capture video frame")

        # Convert the frame to a PIL image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Add play button overlay
        width, height = image.size
        play_button_size = min(width, height) // 4
        play_button = Image.open("C:/Users/vurun/Desktop/App/play_button.png").resize((play_button_size, play_button_size))
        play_button_pos = ((width - play_button_size) // 2, (height - play_button_size) // 2)
        image.paste(play_button, play_button_pos, play_button)

        return image,video_file

    @staticmethod
    def play_video(event,video_data):
        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(video_data))
        else:
            subprocess.call(('xdg-open', os.path.abspath(video_data)))

    @staticmethod
    def open_image(event,image_data):
        # Save video data to a temporary file
        if not os.path.exists('temporary'):
            os.makedirs('temporary')
        image_file = 'temporary/temp_image.png'
        with open(image_file, 'wb') as f:
            f.write(image_data)

        if not os.path.exists(image_file):
            print(f"Error: {image_file} does not exist after writing.")
            return

        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(image_file))
        else:
            subprocess.call(('xdg-open', os.path.abspath(image_file)))

if __name__=='__main__':
    def Image_Reader_default(img_blob):
        print("READER 2")
        image = np.array(Image.open(io.BytesIO(img_blob)))

        reader = easyocr.Reader(['rs_latin','en'])
        result = reader.readtext(image, detail=0)

        def extend_variable(i, variable, searchlist, image_text):
            j = i + 1
            while j < len(image_text) and not any((image_text[j]).startswith(prefix) for prefix in searchlist):
                variable += (" " + image_text[j])
                j += 1
            return variable

        # Initialize variables
        OUTPUT = {  "Datum Operacije": None,
                    "Dg Glavna": list(),
                    "Dg Sporedna": list(),
                    "Dg Latinski": None,
                    "Operator": list(),
                    "Asistenti": list(),
                    "Anesteziolog": list(),
                    "Anestetičar": list(),
                    "Instrumentarka": list(),
                    "Gostujući Specijalizant":list()   }
        
        DoctorsImage_dict = {"Operator":("Operator",["Operator"]),
                             "Asist":("Asistenti",["Asistent 1","Asistent 2","Asistent 3","Asistent"]),
                            "Anestezio":("Anesteziolog",["Anesteziolog"]),
                            "Anestet":("Anestetičar",["Anestetičar","Anesteticar"]),
                            "Instru":("Instrumentarka",["Instrumentarka"]),
                            "Gostuju": ("Gostujući Specijalizant",["Gostujući specijalizant","Gostujuci specijalizant"])}

        prosao_datum=False
        for i, detection in enumerate(result):
            print(i,": ",detection)
            if prosao_datum is False and detection in ['PACIJENT','OPERACIONA LISTA','godište']:
                prosao_datum = True
            if not OUTPUT["Datum Operacije"] or prosao_datum is False:
                date = Media.is_date(detection)
                if date:
                    OUTPUT['Datum Operacije'] = date
                    prosao_datum = True

            if "Glavna operativna dijagnoza" in detection:
                try:
                    mkb = detection.split(' ')[3]
                except IndexError:
                    continue
                MKB = Media.mkb_fix(mkb)
                OUTPUT['Dg Glavna'].append(MKB)

                if not OUTPUT['Dg Latinski']:
                    try:
                        Dg_Latinski = detection.split(mkb)[1].strip()
                        Dg_Latinski = extend_variable(i, Dg_Latinski, ["Glavn", "Spored", "Operac"], result)
                        OUTPUT['Dg Latinski'] = Dg_Latinski
                    except IndexError:
                        print(detection)

            elif "Sporedna operativna dijagnoza" in detection:
                try:
                    mkb = detection.split(' ')[3]
                except IndexError:
                    continue
                MKB = Media.mkb_fix(mkb)
                OUTPUT['Dg Sporedna'].append(MKB)
                
            else: # DOCTORS
                for prefix,(doctorType,fixlist) in DoctorsImage_dict.items():
                    if detection.capitalize().startswith(prefix):
                        for fix in fixlist+['-',',','.',':',';']:
                            detection = detection.replace(fix,"")
                        doctors = extend_variable(i, detection, list(DoctorsImage_dict.keys())+["Preme","Anestez"], result)
                        doctors = doctors.strip()
                        if prefix == 'Gostuju':
                            DOCTORS = []
                            doctors = doctors.split(' ')
                            for i,doc in enumerate(doctors):
                                if doc in ['Dr','dr']:
                                    DOCTORS.append(" ".join(doctors[i:i+3]))
                            if DOCTORS:
                                for doc in DOCTORS:
                                    doc:str
                                    doc = doc.replace("-","")
                                    doc.strip()
                                    
                                OUTPUT[doctorType] += DOCTORS
                        else:
                            if doctors:
                                OUTPUT[doctorType] += [doctors]
        return OUTPUT
    
    print("Start")
    from E_SQLite import Database
    from C_GoogleDrive import GoogleDrive
    db = Database('RHMH.db')
    gd = GoogleDrive()
    GoogleID = db.execute_selectquery(f"SELECT image_data FROM slike WHERE id_slike = 1509")[0][0]
    image_blob = gd.download_BLOB(GoogleID)

    start = time.time()
    reader_def = Image_Reader_default(image_blob)
    Reader_default = f"{time.time()-start:,.2f} s"

    start1 = time.time()
    reader = Media.Image_Reader(image_blob)
    Reader_new =  f"{time.time()-start1:,.2f} s"

    FALSE = []
    for i,(k,v) in enumerate(reader.items()):
        print(i," -"*66)
        print(f"new-{k}: {v}")
        print(f"default-{k}: {reader_def[k]}")
        if v!=reader_def[k]:
            FALSE.append(i)
    print('---'*33)    
    print(FALSE)

    print(f"READER New {Reader_new}")
    print(f"READER Default {Reader_default}")
    #for b in reader:
        #print(f"{b}")

    #for b in reader2:
        #print(f"{b}")

