from datetime import datetime

# Dobij trenutno vreme
trenutno_vreme = datetime.now()

formatirano_vreme = trenutno_vreme.strftime("%Y-%m-%d %H:%M:%S")
print("Trenutno vreme:", formatirano_vreme)

# Dobij dan, mesec, godinu
dan = trenutno_vreme.day
mesec = trenutno_vreme.month
godina = trenutno_vreme.year
print("Dan:", dan)
print("Mesec:", mesec)
print("Godina:", godina)