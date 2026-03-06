from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import glob
from Blockchain import *
from Block import *
from datetime import date
import cv2
import numpy as np
import base64
import random
from datetime import datetime
from PIL import Image
from sendmail import sendmail
import random
import pickle

# Database Configuration - UPDATE THIS WITH YOUR MYSQL PASSWORD
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Alan12345',  # ⚠️ CHANGE THIS TO YOUR MYSQL PASSWORD
    'database': 'evoting',
    'charset': 'utf8'
}

# ensure the addparty table has an 'active' column to support deactivation/reactivation
#
def ensure_active_column():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        # check if column exists
        cur.execute("SHOW COLUMNS FROM addparty LIKE 'active'")
        if cur.rowcount == 0:
            cur.execute("ALTER TABLE addparty ADD COLUMN active TINYINT(1) DEFAULT 1")
            conn.commit()
        conn.close()
    except Exception as e:
        print("Warning: could not ensure active column:", e)

# call once at import time
ensure_active_column()

global username, password, contact, email, address

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)
    fileinput.close()

face_detection = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face_LBPHFaceRecognizer.create()

def votepage(request):
    if request.method == 'GET':
       return render(request, 'VotePage.html', {})
    
def OTPValidation(request):
    if request.method == 'GET':
       return render(request, 'OTPValidation.html', {})
    
def generate_otp(length=4):
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp

      

def AddParty(request):
    if request.method == 'GET':
       parties = []
       try:
           db_connection = pymysql.connect(**DB_CONFIG)
           db_cursor = db_connection.cursor()
           db_cursor.execute("SELECT DISTINCT partyname FROM addparty")
           rows = db_cursor.fetchall()
           parties = [row[0] for row in rows]
           db_connection.close()
       except:
           parties = []
       context = {'parties': parties}
       return render(request, 'AddParty.html', context)

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def CastVote(request):
    if request.method == 'GET':
       return render(request, 'CastVote.html', {})
    

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})
    
def WebCam(request):
    if request.method == 'GET':
        data = str(request)
        formats, imgstr = data.split(';base64,')
        imgstr = imgstr[0:(len(imgstr)-2)]
        data = base64.b64decode(imgstr)
        if os.path.exists("EVotingApp/static/photo/test.png"):
            os.remove("EVotingApp/static/photo/test.png")
        with open('EVotingApp/static/photo/test.png', 'wb') as f:
            f.write(data)
        f.close()
        context= {'data':"done"}
        return HttpResponse("Image saved")    

def checkUser(name):
    flag = 0
    for i in range(len(blockchain.chain)):
          if i > 0:
              b = blockchain.chain[i]
              data = b.transactions[0]
              print(data)
              arr = data.split("#")
              if arr[0] == name:
                  flag = 1
                  break
    return flag            

def getOutput(status):
    global username
    # Show user's registered face at the top
    output = '<div style="margin-bottom: 30px; padding: 20px; background: #f9fafb; border-radius: 12px; display: flex; align-items: center; gap: 20px;">'
    output += '<div style="flex-shrink: 0;"><img src="/static/profiles/'+username+'.png" style="width:100px; height:100px; object-fit:cover; border-radius:50%; border: 3px solid #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);" onerror="this.style.display=\'none\';"></div>'
    output += '<div><h3 style="margin: 0 0 8px 0; color: #1f2937;">'+status+'</h3><p style="margin: 0; color: #6b7280;">Your registered identity has been verified. Please select your candidate below.</p></div></div>'
    
    # Modern table for candidates
    output += '<table class="table">'
    output+='<thead><tr><th>Candidate Name</th>'
    output+='<th>Party Name</th>'
    output+='<th>Area Name</th>'
    output+='<th>Party Image</th>'
    output+='<th>Cast Vote</th></tr></thead><tbody>'
    con = pymysql.connect(**DB_CONFIG)
    with con:
        cur = con.cursor()
        cur.execute("select * FROM addparty")
        rows = cur.fetchall()
        for row in rows:
            cname = row[0]
            pname = str(row[1])
            area = row[2]
            image = row[3]
            # Use party name for image filename
            img_html = '<img src="/static/parties/'+pname+'.png" style="width:150px; height:150px; object-fit:cover; border-radius:8px;" '
            img_html += 'onerror="this.onerror=null; this.src=\'/static/parties/'+pname+'.jpg\'; this.onerror=function(){this.style.display=\'none\'; this.parentNode.innerHTML=\'No Image\';};">'
            output+='<tr><td>'+cname+'</td>'
            output+='<td>'+pname+'</td>'
            output+='<td>'+area+'</td>'
            output+='<td>'+img_html+'</td>'
            output+='<td><a href="FinishVote?id='+cname+'" class="btn btn-primary" style="display:inline-block; padding:8px 16px; text-decoration:none;">Vote</a></td></tr>'
    output+="</tbody></table>"        
    return output      
    

def OTPAction(request):
    if request.method == 'POST':
      global username, password, contact, email, address
      otp = request.POST.get('otp', False)
      status = 'none'
      matched_username = None
      con = pymysql.connect(**DB_CONFIG)
      with con:
        cur = con.cursor()
        cur.execute("select * FROM otp")
        rows = cur.fetchall()
        for row in rows:
            # Check if OTP matches, and get the username from the row
            if int(row[1]) == int(otp):
                status = 'success'
                matched_username = row[0]
                username = matched_username  # Set global username
                print("OTP validated for user:", username)             
                break 
      if status == 'success' and matched_username:
            print("Redirecting to vote page for user:", matched_username)        
            output = getOutput("User predicted as : "+matched_username+"<br/><br/>")
            print(output)
            context= {'data':output}            
            return render(request, 'VotePage.html', context)
      else:
            context= {'data':'Invalid OTP'}
            return render(request, 'OTPValidation.html', context) 
      

def DeactivateParty(request):
    if request.method == 'GET':
        cname = request.GET.get('id', False)
        if cname:
            conn = pymysql.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("UPDATE addparty SET active=0 WHERE candidatename=%s", (cname,))
            conn.commit()
            conn.close()
        return ViewParty(request)


def ReactivateParty(request):
    if request.method == 'GET':
        cname = request.GET.get('id', False)
        if cname:
            conn = pymysql.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("UPDATE addparty SET active=1 WHERE candidatename=%s", (cname,))
            conn.commit()
            conn.close()
        return ViewParty(request)


def DeleteParty(request):
    if request.method == 'GET':
        cname = request.GET.get('id', False)
        if cname:
            conn = pymysql.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("DELETE FROM addparty WHERE candidatename=%s", (cname,))
            conn.commit()
            conn.close()
            # also remove image files
            folder = 'EVotingApp/static/parties/'
            for ext in ['.png', '.jpg', '.jpeg']:
                path = os.path.join(folder, cname+ext)
                if os.path.exists(path):
                    os.remove(path)
        return ViewParty(request)


def FinishVote(request):
    if request.method == 'GET':
        global username
        cname = request.GET.get('id', False)
        voter = ''
        today = date.today()
        data = str(username)+"#"+str(cname)+"#"+str(today)
        blockchain.add_new_transaction(data)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        print("Previous Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Hash : "+str(b.hash))
        bc = "Previous Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Hash : "+str(b.hash)
        blockchain.save_object(blockchain,'blockchain_contract.txt')
        context= {'data':'<font size=3 color=black>Your Vote Accepted<br/>'+bc}
        return render(request, 'UserScreen.html', context)
    
def getUserImages():
    names = []
    ids = []
    faces = []
    dataset = "EVotingApp/static/profiles"
    count = 0
    for root, dirs, directory in os.walk(dataset):
        for j in range(len(directory)):
            pilImage = Image.open(root+"/"+directory[j]).convert('L')
            imageNp = np.array(pilImage,'uint8')
            name = os.path.splitext(directory[j])[0]
            names.append(name)
            faces.append(imageNp)
            ids.append(count)
            count = count + 1
    print(str(names)+" "+str(ids))        
    return names, ids, faces        


def getName(predict, ids, names):
    name = "Unable to get name"
    for i in range(len(ids)):
        if ids[i] == predict:
            name = names[i]
            break
    return name    

def ValidateUser(request):
    if request.method == 'POST':
        global username
        status = "Face not clear. Please retake and then refresh."
        img = cv2.imread('EVotingApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        status = "Face not clear. Please retake and then refresh."
        #for (x, y, w, h) in faces:
        #    face_component = gray[y:y+h, x:x+w]
        if len(faces) == 0:
            context= {'data':'No face detected. Please ensure your face is clearly visible and try again.'}
            return render(request, 'CastVote.html', context)
        faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces
        face_component = gray[fY:fY + fH, fX:fX + fW]
        if face_component is not None:
            names, ids, faces = getUserImages()
            recognizer.train(faces, np.asarray(ids))
            predict, conf = recognizer.predict(face_component)
            print(str(predict)+" === "+str(conf))
            if(conf < 80):
                validate_user = getName(predict, ids, names)
                print(str(validate_user)+" "+str(username))
                if validate_user == username:
                    status = "success"
        else:
            status = "Face not clear. Please retake and then refresh."
        if status == "success":
            flag = checkUser(username)
            if flag == 0:                
                otp = generate_otp()
                print(otp)
                db_connection1 = pymysql.connect(**DB_CONFIG)
                db_cursor1 = db_connection1.cursor()
                student_sql_query1 ="select email FROM register where username='"+username+"'"
                db_cursor1.execute(student_sql_query1)
                db_connection1.commit()  
                rows = db_cursor1.fetchall()
                user_email = rows[0][0]
                print(f"User email: {user_email}")
                
                # Send OTP via email
                email_sent = sendmail(user_email, otp)
                
                # Store OTP in database regardless of email status
                db_connection = pymysql.connect(**DB_CONFIG)
                db_cursor = db_connection.cursor()
                student_sql_query = "INSERT INTO otp(username,otp) VALUES('"+username+"','"+otp+"')"
                db_cursor.execute(student_sql_query)
                db_connection.commit()
                
                if email_sent:
                    context= {'data':'Welcome '+username+'. OTP sent to your email.'}
                else:
                    # If email fails, show OTP on screen for testing
                    context= {'data':'Welcome '+username+'. Email failed. Your OTP is: '+otp+' (Check console for details)'}
                    print(f"[WARNING] EMAIL FAILED - OTP for {username}: {otp}")
                
                return render(request, 'OTPValidation.html', context)
               # return render(request, 'VotePage.html', context)
            else:
                context= {'data':"You already casted your vote"}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':status}
            return render(request, 'CastVote.html', context)
        

def getCount(name):
    count = 0
    cname=name
    for i in range(len(blockchain.chain)):
          if i > 0:
              print("dddddddddddddddddddddddddddddd")
              print(i)
              b = blockchain.chain[i]             
              data = b.transactions[0]            
              arr = data.split("#")
              print(arr)
              #print(len(arr))
              print(cname)
              print(arr[1])
              if arr[1] == name:
                  count = count + 1
                  #print(arr[i])
                  print(count)
    return count

#finding party
def find_party_image(cname, image):
    """Find the actual image filename by scanning the parties folder"""
    party_folder = 'EVotingApp/static/parties/'
    
    # Images are stored by candidate name - try exact match first, then case-insensitive
    candidates_to_try = [cname, image, cname.lower(), image.lower()]
    
    for candidate in candidates_to_try:
        
        files = glob.glob(f"{party_folder}{candidate}.*")
        if files:
            filename = os.path.basename(files[0])
            print(f"DEBUG: Found image {filename} for candidate {cname}")
            return filename
    
    print(f"DEBUG: No image found for candidate {cname} in {party_folder}")
    return None

def ViewVotes(request):
    if request.method == 'GET':
        output = '<table class="table">'
        output+='<thead><tr><th>Candidate Name</th>'
        output+='<th>Party Name</th>'
        output+='<th>Area Name</th>'
        output+='<th>Image</th>'
        output+='<th>Vote Count</th></tr></thead><tbody>'
        con = pymysql.connect(**DB_CONFIG)
        with con:
            cur = con.cursor()
            # only show active parties during voting
            cur.execute("select * FROM addparty WHERE active=1")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                count = getCount(cname)
                pname = str(row[1])
                area = row[2]
                image = row[3]
                active_flag = row[4] if len(row) > 4 else 1
                # Find the actual image file using helper function
                img_file = find_party_image(cname, image)
                if img_file:
                    img_src = '/static/parties/'+img_file
                else:
                    img_src = '/static/parties/no-image.png'
                img_html = '<img src="'+img_src+'" style="width:150px; height:150px; object-fit:cover; border-radius:8px;" '
                img_html += 'onerror="this.style.display=\'none\'; this.parentNode.innerHTML=\'No Image\';">'
                status_text = 'Active' if active_flag == 1 else 'Inactive'
                if active_flag == 1:
                    action_link = '<a href="DeactivateParty?id='+cname+'" class="btn btn-warning">Deactivate</a>'
                else:
                    action_link = '<a href="ReactivateParty?id='+cname+'" class="btn btn-success">Reactivate</a>'
                action_link += ' <a href="DeleteParty?id='+cname+'" class="btn btn-danger" onclick="return confirm(\'Delete this party?\')">Delete</a>'
                output+='<tr><td>'+cname+'</td>'
                output+='<td>'+pname+'</td>'
                output+='<td>'+area+'</td>'
                output+='<td>'+status_text+'</td>'
                output+='<td>'+img_html+'</td>'
                output+='<td>'+action_link+'</td></tr>'
        output+="</tbody></table>"        
        context= {'data':output}
        return render(request, 'ViewVotes.html', context)    
            
def ViewParty(request):
    if request.method == 'GET':
        output = '<table class="table">'
        output+='<thead><tr><th>Candidate Name</th>'
        output+='<th>Party Name</th>'
        output+='<th>Area Name</th>'
        output+='<th>Status</th>'
        output+='<th>Image</th>'
        output+='<th>Actions</th></tr></thead><tbody>'
        con = pymysql.connect(**DB_CONFIG)
        with con:
            cur = con.cursor()
            cur.execute("select * FROM addparty")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                pname = str(row[1])
                area = row[2]
                image = row[3]
                # Find the actual image file using helper function
                img_file = find_party_image(cname, image)
                if img_file:
                    img_src = '/static/parties/'+img_file
                else:
                    img_src = '/static/parties/no-image.png'
                img_html = '<img src="'+img_src+'" style="width:150px; height:150px; object-fit:cover; border-radius:8px;" '
                img_html += 'onerror="this.style.display=\'none\'; this.parentNode.innerHTML=\'No Image\';">'
                status_text = 'Active' if row[4] == 1 else 'Inactive'
                # action links
                if row[4] == 1:
                    action_link = '<a href="DeactivateParty?id='+cname+'" class="btn btn-warning">Deactivate</a>'
                else:
                    action_link = '<a href="ReactivateParty?id='+cname+'" class="btn btn-success">Reactivate</a>'
                action_link += ' <a href="DeleteParty?id='+cname+'" class="btn btn-danger" onclick="return confirm(\'Delete this party?\')">Delete</a>'
                output+='<tr><td>'+cname+'</td>'
                output+='<td>'+pname+'</td>'
                output+='<td>'+area+'</td>'
                output+='<td>'+status_text+'</td>'
                output+='<td>'+img_html+'</td>'
                output+='<td>'+action_link+'</td></tr>'
        output+="</tbody></table>"        
        context= {'data':output}
        return render(request, 'ViewParty.html', context)    

def AddPartyAction(request):
    if request.method == 'POST':
      cname = request.POST.get('t1', False)
      pname = request.POST.get('t2', False)
      area = request.POST.get('t3', False)
      myfile = request.FILES['t4']

      fs = FileSystemStorage()
      filename = fs.save('EVotingApp/static/parties/'+cname+'.png', myfile)
      
      db_connection = pymysql.connect(**DB_CONFIG)
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO addparty(candidatename,partyname,areaname,image,active) VALUES('"+cname+"','"+pname+"','"+area+"','"+cname+"',1)"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Party Details Added'}
       return render(request, 'AddParty.html', context)
      else:
       context= {'data':'Error in adding party details'}
       return render(request, 'AddParty.html', context)    

def saveSignup(request):
    if request.method == 'POST':
        global username, password, contact, email, address
        img = cv2.imread('EVotingApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(gray, 1.3,5)
        for (x, y, w, h) in faces:
            face_component = img[y:y+h, x:x+w]
        if face_component is not None:
            cv2.imwrite('EVotingApp/static/profiles/'+username+'.png',face_component)
            db_connection = pymysql.connect(**DB_CONFIG)
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                context= {'data':'Signup Process Completed'}
                return render(request, 'Register.html', context)
            else:
                context= {'data':'Unable to detect face. Please retry'}
                return render(request, 'Register.html', context)
        else:
            context= {'data':'No face detected. Please try again.'}
            return render(request, 'CaptureFace.html', context)


def Signup(request):
    if request.method == 'POST':
      global username, password, contact, email, address
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      
      # Check if username already exists
      try:
          con = pymysql.connect(**DB_CONFIG)
          with con:
              cur = con.cursor()
              cur.execute("SELECT username FROM register WHERE username = %s", (username,))
              if cur.fetchone():
                  context = {'data': 'Username already exists. Please choose another.'}
                  return render(request, 'Register.html', context)
      except Exception as e:
          print(f"Database error during signup: {e}")
      
      context= {'data':'Capture Your face'}
      return render(request, 'CaptureFace.html', context)
      
def AdminLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Admin.html', context)

def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        con = pymysql.connect(**DB_CONFIG)
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    db_connection1 = pymysql.connect(**DB_CONFIG)
                    db_cursor1 = db_connection1.cursor()
                    student_sql_query1 = "delete from otp"
                    db_cursor1.execute(student_sql_query1)
                    db_connection1.commit()
                    status = 'success'
                    break
        if status == 'success':
            context= {'data':'<center><font size="3" color="black">Welcome '+username+'<br/><br/><br/><br/><br/>'}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)





        
            
