from wifi import Cell, Scheme

print(list(Cell.all('wlan0')))

schemes = list(Scheme.all())
print (schemes)
