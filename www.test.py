import sqlite3
from GoogleDrive import GoogleDrive_Communication
from variables import RHMH_DB,MIME,GoogleDrive_Slike
# Povezivanje sa bazom podataka
google = GoogleDrive_Communication()
google.download_file(RHMH_DB['id'],"RHMH.db")

conn = sqlite3.connect("RHMH.db")
c = conn.cursor()

# Dodavanje nove kolone
c.execute("SELECT * from slike")  # Za float
t = c.fetchall()
for i in t:
    ID = i[5]
    FORMAT = MIME[i[4].split('-')[1]]
    google.get_file_info(ID)
    print(i)

# Čuvanje promena
conn.commit()

# Zatvaranje konekcije
conn.close()

google.update_file(RHMH_DB['id'],"RHMH.db",RHMH_DB['mime'])
#'''