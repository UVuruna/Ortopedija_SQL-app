from PIL import Image, ImageTk, ImageDraw
import cv2
import io
import pillow_heif
import subprocess
import os
import easyocr
from datetime import datetime
import numpy as np

# Registracija HEIF formata
pillow_heif.register_heif_opener()

def is_date(date_string):
    try:
        # Pokušaj parsiranja stringa u format 'dd.mm.yyyy.'
        datetime.strptime(str(date_string), '%d.%m.%Y.')
        return True
    except ValueError:
        return False

def Image_Reader(img_blob,PRINT=False):
    image = np.array(Image.open(io.BytesIO(img_blob)))

    reader = easyocr.Reader(['hr', 'sl', 'bs', 'en'])
    result = reader.readtext(image, detail=0)

    def extend_variable(i, variable, searchlist, image_text):
        j = i + 1
        while j < len(image_text) and not any(image_text[j].startswith(prefix[:4]) for prefix in searchlist):
            variable += (" " + image_text[j])
            j += 1
        return variable

    # Initialize variables
    Ime = None
    Prezime = None
    Godiste = None
    Dg_Glavna = []
    Dg_Sporedna = []
    Dg_Latinski = None
    Datum_Operacije = None
    staff = ["Operator", "Asistent 1", "Asistent 2", "Asistent 3",
             "Anesteziolog", "Anestetičar", "Instrumentarka",
             "Gostujući specijalizant"]
    staff_dict = {}

    for i, detection in enumerate(result):
        if is_date(detection.strip()):
            Datum_Operacije = detection.strip()
        elif detection.title().startswith('Pac'):
            j = i+1
            imeprezime = result[j].split(' ')
            Ime = imeprezime[0].capitalize()
            if len(imeprezime) > 1:
                if len(imeprezime)==2:
                    Prezime = imeprezime[1].capitalize()
                elif len(imeprezime)==3:
                    Prezime = imeprezime[2].capitalize()
            else:
                j+=1
                newrow = result[j].split(' ')
                if len(newrow)==1:
                    Prezime = newrow[0].capitalize()
                elif len(newrow)==2:
                    Prezime = newrow[1].capitalize()
            j+=1
            if result[j][0].isdigit():
                try:
                    Godiste = int(result[j])
                except:
                    Godiste = result[j].replace('.','')

        elif "Glavna operativna dijagnoza" in detection:
            mkb = detection.split(' ')[3]
            Dg_Glavna.append("S"+mkb[1:] if mkb[0] in ['5','8'] \
                              else "Z"+mkb[1:] if mkb[0]=='2' else mkb)
            if not Dg_Latinski:
                Dg_Latinski = detection.split(mkb)[1].strip()
                Dg_Latinski = extend_variable(i, Dg_Latinski, ["Glavna", "Sporedna", "Operacije"], result)

        elif "Sporedna operativna dijagnoza" in detection:
            mkb = detection.split(' ')[3]
            Dg_Sporedna.append("S"+mkb[1:] if mkb[0] in ['5','8'] \
                              else "Z"+mkb[1:] if mkb[0]=='2' else mkb)
        else:
            for st in staff:
                if detection.capitalize().startswith(st):
                    doctors = detection.replace(f'{st}:', '') \
                        if ':' in detection \
                            else detection.replace(f'{st}', '')
                    if 'lekar na specijalizaciji' in doctors:
                        doctors = doctors.replace('lekar na specijalizaciji','')
                    if '-' in doctors:
                        doctors = doctors.replace('-','')
                    if "," in doctors:
                        doctors = [i.strip() for i in doctors.split(",")]
                        staff_dict[st] = doctors
                    elif ";" in doctors:
                        doctors = [i.strip() for i in doctors.split(";")]
                        staff_dict[st] = doctors
                    elif ":" in doctors:
                        doctors = [i.strip() for i in doctors.split(":")]
                        staff_dict[st] = doctors
                    else:
                        if st not in staff_dict:
                            staff_dict[st] = []

                        if st!="Gostujući specijalizant":
                            doctors = extend_variable(i, doctors, staff+["Premedikacija"], result).strip()
                            staff_dict[st] = [doctors]
                        else:
                            extra = extend_variable(i, doctors, staff+["Premedikacija"], result).replace(doctors,"")
                            staff_dict["Gostujući specijalizanti"] = [doctors.strip(),extra.strip()] if extra else [doctors.strip()]
                            
        if PRINT:                
            print(i, ': ', detection)

    if PRINT:
        print('---' * 20)
        print("Datum_Operacije: ", Datum_Operacije)
        print("Ime: ", Ime)
        print("Prezime: ", Prezime)
        print("Godiste: ", Godiste)
        print("Dg_Glavna: ", Dg_Glavna)
        print("Dg_Sporedna: ", Dg_Sporedna)
        print("Dg_Latinski: ", Dg_Latinski)
        for k, v in staff_dict.items():
            if v[0]:
                print(f"{k}: {v}")
    STAFF = {}
    for k,v in staff_dict.items():
        if v[0]:
            if "Asistent" in k:
                if "Asistent" not in STAFF:
                    STAFF["Asistenti"] = []
                    STAFF["Asistenti"].append(v[0])
            else:
                STAFF[k] = v

    STAFF.update({"Ime": Ime,
            "Prezime": Prezime,
            "Godište": Godiste,
            "Datum Operacije": Datum_Operacije,
            "Dg Glavna": Dg_Glavna,
            "Dg Sporedna": Dg_Sporedna,
            "Dg Latinski": Dg_Latinski})
    return STAFF




def get_image(image_blob_data): # Format za Canvas
    image = Image.open(io.BytesIO(image_blob_data))
    return image
    return ImageTk.PhotoImage(image)

def resize_image(image, max_width, max_height):
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    scale_ratio = min(width_ratio, height_ratio)

    new_width = int(image.width * scale_ratio)
    new_height = int(image.height * scale_ratio)
    return image.resize((new_width, new_height), Image.LANCZOS),new_width,new_height

def image_for_canvas(image): # Format za Canvas
    return ImageTk.PhotoImage(image)

def create_video_thumbnail_with_play_button(video_data):
    # Save video data to a temporary file
    video_file = 'temp_video.mp4'
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

    return image

def play_video(event,video_data):
    # Save video data to a temporary file
    video_file = 'temp_video.mp4'
    with open(video_file, 'wb') as f:
        f.write(video_data)

    # Open the video in the default viewer
    if os.name == 'nt':  # For Windows
        os.startfile(video_file)
    else:
        subprocess.call(('xdg-open', video_file))
