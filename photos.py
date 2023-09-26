import os 
from datetime import datetime

folder_path = "fotos_lou"
file_list = []
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        file_list.append([file_path,datetime.fromtimestamp(os.path.getctime(file_path))])
print(file_list)