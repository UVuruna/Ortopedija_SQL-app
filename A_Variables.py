
FONT = "Montserrat"
F_SIZE = 11

app_name = "Restruktivna Hirurgija Ortopedije"
title_Txt = "Pacijenti RHMH"
form_title = "Pacijent"
font_title = (FONT, int(F_SIZE*3.7), "bold")
font_groups = (FONT, int(F_SIZE*1.8), "bold")
font_label = lambda b="bold": (FONT, int(F_SIZE*1.1), b)
font_entry = (FONT, F_SIZE)

title_height = 180

THEME = 'uv13'

def_font = (FONT, F_SIZE)


labelColor = "light" if THEME!='uv12' else "active"
titleTxtColor = "light" if THEME!='uv12' else "primary"
dangerButtTxtColor = "active" if THEME!='uv12' else "dark"
bootstyle_table = "primary"
bootstyle_check = "primary"


# >>> PADDING <<<
shape_padding = ((6,6),(0,6))
main_title_padding = ((12,12),(12,12))
title_padding = ((0,0),(6,6))
form_padding_entry = ((3,12),(3,3))
search_padding = ((3,3),(3,3))
form_padding_button = ((6,6),(6,6))

#  >>> BORDER <<<
bd_entry = 2
bd_main_frame = 4
bd_inner_frame = 3

#  >>> FORM <<<
form_small_width = 7
form_medium_width = 18
form_large_width = 25
form_date_width = 13

form_butt_width = 80
form_butt_height = 40

#  >>> SEARCH BAR <<<

search_1_width = 18
search_2_width = 10

search_butt_width = 10

title_ImgData = ("C:/Users/vurun/Desktop/App/GodHand_Transparent_smallest.png",0.007,0.033)

form_name = "Pacijent"
form_groups = {"Default": {"start":4,"Dijagnoza":3, "Hospitalizacija":None},"Alternative": {"start":1,"Doktori":5,"Slike":None}}

default_form_entry = { "Ime": ("Ime", 'StringVar', form_medium_width),
                    "Prezime": ("Prezime", 'StringVar', form_medium_width),
                    "Godište": ("Godište", 'StringVar', form_small_width),
                    "Pol": ("Pol", 'Combobox', form_small_width, ("Muško", "Žensko")),
                    "Dg Glavna": ("Glavna", 'Validate', form_large_width),
                    "Dg Sporedna": ("Sporedna", 'Validate', form_large_width),
                    "Dg Latinski": ("Latin", 'Text', form_large_width),
                    "Datum Prijema": ("Prijem", 'DateEntry', form_date_width),
                    "Datum Operacije": ("Operacija", 'DateEntry', form_date_width),
                    "Datum Otpusta": ("Otpust", 'DateEntry', form_date_width)        }

alternative_form_entry = {   "Patient Info":("","Info"),
                            "Operator": ("Operator", 'StringVar', form_large_width-3),
                            "Anesteziolog": ("Anesteziolog", 'StringVar', form_large_width-3),
                            "Anestetičar": ("Anestetičar", 'StringVar', form_large_width-3),
                            "Asistenti": ("Asistenti", 'Text', form_large_width-3),
                            "Gostujući Specijalizanti": ("Gostujući\nSpecijalizanti", 'Text', form_large_width-3),
                             "Slike":("","Slike") }

default_form_buttons = [("ADD",None),
                        ("UPDATE",None),
                        ("DELETE","danger"),
                        ("CLEAR\nFORM","warning")]

alternative_form_buttons = [("ADD\nIMAGE",None),
                            ("UPDATE\nIMAGE",None),
                            ("DELETE\nIMAGE",'danger'),
                            ("SHOW\nIMAGES",'info'),
                            ("DOWNLOAD\nIMAGE",'info'),
                            ("FILL FROM\nIMAGE",'info')]

MKB_Entry = {"MKB - šifra":("MKB",7),
             "Opis Dijagnoze":("Opis\nDijagnoze",60),
             "Buttons":[
                 ("ADD",None),
                 ("UPDATE",None),
                 ("DELETE","danger"),
                 ("IMPORT\nMANY","warning")]}

max_searchby = 5

IMAGES = {"Swap":[("C:/Users/vurun/Desktop/App/swap.png",33,33),("C:/Users/vurun/Desktop/App/swap_hover.png",33,33)],
          "Hide":[("C:/Users/vurun/Desktop/App/hide.png",48,33),("C:/Users/vurun/Desktop/App/hide_hover5.png",48,33)]}

ThemeColors_Dict = {}

GoogleDrive_Slike = ['1e-KyYcDIt_V2Gn79blz0gESZLpeV4xVn']
GoogleDrive_DB = ['1ybEVItyB75BParYUN2-ab_oVe2tBj1NW']
RHMH_DB = {'id':'1cwOFgPjVRhj6qQ9335RJVdkUkBhSvcJ8','mime':'application/x-sqlite3'}

MIME = {'PNG' : 'image/png',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}