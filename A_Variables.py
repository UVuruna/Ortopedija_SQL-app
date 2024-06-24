# B_Decorators
from datetime import datetime, date
import time
import functools
import traceback

# C_GoogleDrive
import io
import os
import pickle
import google.auth
from google.auth.transport.requests import AuthorizedSession, Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# D_SQLite_Connection
import sqlite3
import sqlparse
from tkinter import simpledialog,messagebox
import ttkbootstrap as tb

# E_SQLite_DBMS
from tkinter import *
from ttkbootstrap import widgets
from ttkbootstrap.dialogs.dialogs import Messagebox
import customtkinter as ctk
import queue

# F_Media_Manipulation
from PIL import Image, ImageTk, ImageDraw
import cv2
import pillow_heif
import subprocess
import easyocr
import numpy as np

# G_Viewer
import json
import inspect
from tkinter.font import nametofont
import threading
from ttkbootstrap.style import Colors

WIDTH = 1782
HEIGHT = 927

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

THEME = 'dark_blue'

def_font = (FONT, F_SIZE)


labelColor = "light" if THEME!='light_blue' else "active"
theme_fg = "light" if THEME!='light_blue' else "dark"
titleTxtColor = "light" if THEME!='light_blue' else "primary"
dangerButtTxtColor = "active" if THEME!='light_blue' else "dark"
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
form_groups = {"Default": {"start":4,"Dijagnoza":3, "Hospitalizacija":None},"Alternative": {"start":1,"Doktori":6,"Slike":None}}

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

alternative_form_entry = {  "Patient Info":("","Info"),
                            "Operator": ("Operator", 'StringVar', form_large_width-4),
                            "Asistenti": ("Asistenti", 'Text', form_large_width-4),
                            "Anesteziolog": ("Anesteziolog", 'StringVar', form_large_width-4),
                            "Anestetičar": ("Anestetičar", 'StringVar', form_large_width-4),
                            "Instrumentarka": ("Instrumentarka", 'StringVar', form_large_width-4),
                            "Gostujući Specijalizant": ("Gostujući\nSpecijalizant", 'Text', form_large_width-4),
                            "Slike":("","Slike"),
                            "Opis":("Opis","StringVar",form_large_width-4) }

default_form_buttons = [("ADD",None),
                        ("UPDATE",None),
                        ("DELETE","danger"),
                        ("CLEAR\nFORM","warning")]

alternative_form_buttons = [("ADD\nIMAGE",None),
                            ("UPDATE\nIMAGE",None),
                            ("DELETE\nIMAGE",'danger'),
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
          "Hide":[("C:/Users/vurun/Desktop/App/hide.png",48,33),("C:/Users/vurun/Desktop/App/hide_hover2.png",48,33)]}

ThemeColors_Dict = {}

GD_Slike_folder = ['1e-KyYcDIt_V2Gn79blz0gESZLpeV4xVn']
GD_RHMH_folder = ['1ybEVItyB75BParYUN2-ab_oVe2tBj1NW']
RHMH_DB = {'id':'1cwOFgPjVRhj6qQ9335RJVdkUkBhSvcJ8','mime':'application/x-sqlite3'}

MIME = {'PNG' : 'image/png',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}

WAIT = 10 # ms
BUTTON_LOCK = 500 # ms