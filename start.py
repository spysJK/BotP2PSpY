import os

os.system('docker build -t "bot" . ')
os.system('docker run bot')