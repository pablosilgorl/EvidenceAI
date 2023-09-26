from flask import Flask, render_template, request, jsonify
import calendar
import re
import maps
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tqdm import tqdm

def is_weekend(date_string):
    # Convert the date string to a datetime object
    date_obj = datetime.strptime(date_string, "%d/%m/%Y")
    
    # Get the day of the week (0 - Monday, 6 - Sunday)
    day_of_week = date_obj.weekday()
    
    # Check if the day is a weekend day (Saturday or Sunday)
    return day_of_week >= 5

def insert_string_in_string(bigstring, smallstring, index):
    return bigstring[:index] + smallstring + bigstring[index:]

def get_max_number_of_messages():
  max_len = 0
  for key, value in messages_by_date.items():
    if len(value) > max_len:
        max_len = len(value)
  return max_len

messages_by_date = {}
keyword = ""

def fill_up_message_dictionary(keyword):
  messages_by_date.clear()
  file_path = 'lou.txt'
  file_lou = []
  with open(file_path, 'r', encoding="utf8") as file:
      # Read the file line by line
      for line in file: 
          message  = line.strip()    
          file_lou.append(message)
  message = ""
  date = "" 
  i=0
  while i < len(file_lou):
      if date == "":
          date = file_lou[i][0:10]
      time = file_lou[i][12:17]
      owner = file_lou[i][19:file_lou[i].find(':', 19)]
      content = file_lou[i][file_lou[i].find(':', 19)+2:]
      if keyword != "" and re.search(keyword,content, re.IGNORECASE):
          pos = re.search(keyword, content, re.IGNORECASE).span()[0]
          content = insert_string_in_string(content, "<mark>", pos)
          content = insert_string_in_string(content, "</mark>", pos+6+len(keyword))
      message += time+" "+owner+": "+content+"\n"
      if i < len(file_lou)-3:
          if len(file_lou[i+1])>10 and file_lou[i+1][2]=="/" and file_lou[i+1][5]=="/":
              if date in messages_by_date:
                  messages_by_date[date].append(message)
              else:
                  messages_by_date[date] = ["<h2 id=\"display-date\">"+date+" MENSAJES</h2>", message]
              message = ""
              date = ""
      i+=1

fill_up_message_dictionary("")
max_number=get_max_number_of_messages()

def is_substring_in_list(substring, string_list):
    for item in string_list:
        if substring in item:
            return True
    return False

def get_messages_count_for_month(year, month):
    cal = calendar.monthcalendar(year, month)
    cal_aux = []
    for week in cal:
        week_aux = []
        for day in week:
            if day == 0:
              week_aux.append(0)
            else:
              messages = messages_by_date.get(f"{day:02d}/{month:02d}/{year}")
              if messages == None:
                  week_aux.append(0)
              elif is_substring_in_list(keyword, messages):
                  week_aux.append(1)
              else:
                  week_aux.append(0)
        cal_aux.append(week_aux)
    return cal_aux

def get_locations_count_for_month(year, month):
    cal = calendar.monthcalendar(year, month)
    cal_aux = []
    for week in cal:
        week_aux = []
        for day in week:
            if day == 0:
              week_aux.append(0)
            else:
              locations = maps.locations_by_date.get(f"{year}-{month:02d}-{day:02d}")
              if locations == None:
                  week_aux.append(0)
              elif is_substring_in_list(maps.city, locations):
                  week_aux.append(1)
              else:
                  week_aux.append(0)
        cal_aux.append(week_aux)
    return cal_aux

def get_photos_for_date(year, month, day):
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    photos = []
    dates = {}
    folder_path = "static/photos"  # Replace with your folder path
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_creation_date = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
            dates[str(file_creation_date)]=""
            if str(file_creation_date) == str(date_str):
                file_creation_time = datetime.fromtimestamp(os.path.getmtime(file_path)).time()
                photos.append({'url': file_path.replace("\\","/"), 'time': str(file_creation_time)  })
    return photos

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def index():
    year = 2023  # Replace with your year
    month = 8    # Replace with your month
    return render_template('index.html', calendar_data=get_month_calendar(year, month), year=year, month=month)

@app.route('/keyword')
def update_keyword():
    global keyword 
    keyword = request.args.get('keyword')
    fill_up_message_dictionary(keyword)
    maps.city = ""
    maps.process_data()
    return jsonify(message="OK")

@app.route('/city')
def update_city(): 
    keyword = ""
    fill_up_message_dictionary(keyword)
    maps.city = request.args.get('city')
    maps.process_data()
    return jsonify(message="OK")

@app.route('/get_photos')
def get_photos():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    
    photos = get_photos_for_date(year, month, day)
    return jsonify(photos)

@app.route('/get_messages')
def get_messages():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    messages = get_messages_for_date(year, month, day)
    return jsonify(messages)

@app.route('/get_locations')
def get_locations():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    locations = get_locations_for_date(year, month, day)
    return jsonify(locations)

@app.route('/get_calendar')
def get_calendar():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    
    cal = calendar.monthcalendar(year, month)
    calendar_data = [[day if day != 0 else '' for day in week] for week in cal]
    return jsonify(calendar_data)

@app.route('/get_messages_count')
def get_messages_count():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    messages_count = get_messages_count_for_month(year, month)
    return jsonify(messages_count)

@app.route('/get_locations_count')
def get_locations_count():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    locations_count = get_locations_count_for_month(year, month)
    return jsonify(locations_count)

def get_month_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    return cal

def get_messages_for_date(year, month, day):
    date = f"{day:02d}/{month:02d}/{year}" 
    messages = messages_by_date.get(date)
    if messages == None:
        return ""
    else:
        return messages_by_date.get(date)

def get_locations_for_date(year, month, day):
    date = f"{year}-{month:02d}-{day:02d}" 
    locations = maps.locations_by_date.get(date)
    if locations == None:
        return ""
    else:
        return locations
def extract_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    return frame

def generate_pdf():
    pdf_file_path = "lou.pdf"
    pdf_content = ""
    number_of_messages = 0
    for year in [2022, 2023]:
        for month in range(1, 13):
            calendar = get_month_calendar(year, month)
            for week in calendar:
                for day in week:
                    if day != 0:
                        day_date = datetime(year, month, day)
                        if maps.start_date <= day_date <= maps.end_date:
                            day_info = f"{day:02d}/{month:02d}/{year}\n"
                            day_info += "\nLOCALISATIONS\n"
                            photo_presence = False
                            location_in_city = False
                            # Append location information
                            for location in get_locations_for_date(year, month, day)[1:]:
                                day_info += str(location) + "\n"
                                if "stanbul" in location or "Auribeau" in location or "Portugal" in location:
                                    location_in_city = True
                            # Append message information
                            messages = ""
                            for message in get_messages_for_date(year, month, day)[1:]:
                                if datetime.strptime("15:00", "%H:%M").time()<datetime.strptime(message[:5], "%H:%M").time() or is_weekend(f"{day:02d}/{month:02d}/{year}"):
                                    messages += str(message)
                                    number_of_messages+=1
                            if messages != "":
                                print(messages)
                                keep = input("\nKeep?(y/n): ")
                                if keep == "y" or keep == "" or keep == "yes":
                                    print("KEEP\n")
                                    day_info += "\nMESSAGES AVEC PABLO\n"
                                    day_info += messages
                            day_info += "\nPHOTOS ET VIDEOS\n"
                            # Append photo information
                            for photo in get_photos_for_date(year, month, day):
                                if "mp4" in photo['url']:
                                    day_info += str(photo['time']) + " " + str(photo['url']) + "\n"
                                    snapshot = photo['url'].replace("mp4","jpg").replace("photos","snapshots")
                                    day_info += f"<image>{snapshot}</image>\n"

                                else:
                                    day_info += str(photo['time']) + " " + str(photo['url']) + "\n"
                                    # Add the actual image to the PDF
                                    day_info += f"<image>{photo['url']}</image>\n"
                                photo_presence = True
                            if location_in_city or photo_presence:
                                pdf_content += day_info + "\n"
    print("Number of messages getting into the pdf:", number_of_messages)
    create_pdf(pdf_file_path, pdf_content)
    exit()

def create_pdf(file_path, content):
    c = canvas.Canvas(file_path, pagesize=letter)

    # Set font and size
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    c.setFont("DejaVuSans", 12)

    # Split content into lines
    lines = content.split('\n')

    # Calculate page height and bottom margin
    page_height = letter[1]
    bottom_margin = 50

    # Initialize y-coordinate and page number
    y = page_height - bottom_margin
    page_num = 1

    # Loop through lines and handle page breaks
    for i in tqdm(range(len(lines))):
    # Check if y-coordinate goes beyond page boundary
        line = lines[i]
        if y < bottom_margin:
            c.showPage()  # Start a new page
            c.setFont("DejaVuSans", 12)
            y = page_height - bottom_margin  # Reset y-coordinate
            page_num += 1

        # If the line contains <image> tag, draw the image
        if "<image>" in line and "</image>" in line:
            if y - 210 < bottom_margin:
              c.showPage()  # Start a new page
              c.setFont("DejaVuSans", 12)
              y = page_height - bottom_margin  # Reset y-coordinate
              page_num += 1
            image_url = line.replace("<image>", "").replace("</image>", "")
            image_width = 200 
            image_height = 150
            image_y = y - image_height - 20  
            c.drawImage(image_url, 25, image_y, width=image_width, height=image_height)
            y -= 210
        else:
            # Draw the line
            if "/" in line and ":" not in line:
                # Set a larger font size for the date
                c.setFont("DejaVuSans", 20)  # Adjust font name and size
                c.drawString(25, y, lines[i])
                c.setFont("DejaVuSans", 12)  # Reset font size
            else:
                # Draw the line
                if len(line) > 85:
                    line_parts = [line[i:i+85] for i in range(0, len(line), 85)]
                    for part in line_parts:
                        c.drawString(25, y, part)
                        y -= 20
                else:
                    # Draw the line
                    c.drawString(25, y, line)  # Adjust x-coordinate here
                    # Move y-coordinate up
                    y -= 20

    # Save the PDF
    c.save()
#generate_pdf()

if __name__ == '__main__':
    app.run(debug=True)