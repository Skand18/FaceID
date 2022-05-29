
from flask import Flask,flash, redirect , render_template , request , session , url_for
from cs50 import SQL
from flask_session import Session
import numpy as np
import cv2
from tempfile import mkdtemp
import zlib
import face_recognition
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from PIL import Image
from base64 import b64decode , b64encode


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///data.db")


images = []
unknown_images=[]
def findEncodings(images):
    encodeList = []
    for img in images:
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


@app.route("/")
def home():
    return redirect("/home")

@app.route("/home")
def index():
     return render_template("index.html")
 
 
@app.route("/login", methods=["GET","POST"])
def login():
      session.clear()
      
      if request.method=="POST":
       
            input_username = request.form.get("username")
            input_password = request.form.get("password")
            
            
            if not input_username:
                return render_template("login.html", messager = 1)
            
            
            elif not input_password:
             return render_template("login.html",messager = 2)
         
         
            username = db.execute("SELECT * FROM users WHERE username = :username",
                              username=input_username)
            
            if len(username) != 1 or not check_password_hash(username[0]["hash"], input_password):
             return render_template("login.html",messager = 3)
         
            session["user_id"] = username[0]["id"]
            
             
            return redirect("/")
        
      else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    
    return redirect("/")

@app.route("/register" , methods=["GET" , "POST"])
def register():
    
    if request.method=="POST":
    
       input_username = request.form.get("username")
       input_password = request.form.get("password")
       input_confirmation = request.form.get("confirmation")
       
       if not input_username:
        return render_template("register.html",messager = 1)
    
       elif not input_password:
            return render_template("register.html",messager = 2)
        
       elif not input_password == input_confirmation:
            return render_template("register.html",messager = 3)
        
       username = db.execute("SELECT username FROM users WHERE username = :username",
                              username=input_username)
       
       if len(username) == 1:
            return render_template("register.html",messager = 5)
        
       else:
           new_user = db.execute("INSERT INTO users (username , hash) VALUES (:username, :password)",
                                  username =input_username,
                                  password = generate_password_hash(input_password, method="pbkdf2:sha256",salt_length =16),)
           if new_user:
               session["user_id"] = new_user
                    
           return redirect("/")
       
    else:
           return render_template("register.html")
       
       
 
@app.route("/facereg", methods=["GET", "POST"])
def facereg():
    session.clear()
    if request.method == "POST":
        
        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        username = request.form.get("name")
        name = db.execute("SELECT * FROM users WHERE username = :username",username=username)
        if len(name) != 1:
            return render_template("camera.html",message = 1)
        
        id_ = name[0]['id']    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        
        decoded_data = b64decode(uncompressed_data)
        
        
        
        new_image_handle = open('./static/face/unknown/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
     
        
        try:
            image_of_bill = face_recognition.load_image_file('./static/face/'+str(id_)+'.jpg')
        except:
            return render_template("camera.html",message = 5)
        
        bill_face_encoding = findEncodings(images)


        try:
            unknown_image = face_recognition.load_image_file('./static/face/unknown/'+str(id_)+'.jpg')
        except:
            return render_template("camera.html",message = 2)
        
        unknown_face_encoding = findEncodings(unknown_images)

        results=[]
       
              
        for known,unknown in zip (bill_face_encoding,unknown_face_encoding):
              results=face_recognition.compare_faces(known, unknown)
             
              results.sort(reverse=True)      
            
              if results[0]:
               username = db.execute("SELECT * FROM users WHERE username = :username", username="swa")
               session["user_id"] = username[0]["id"]
               return redirect("/")

              else:
                 return render_template("camera.html",message=3)
          
        return redirect("/")         
            

    else:
        return render_template("camera.html")
    
    
    
  
@app.route("/facesetup", methods=["GET", "POST"])
def facesetup():
    if request.method == "POST":
        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        
        id_=db.execute("SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["id"]
     
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        decoded_data = b64decode(uncompressed_data)
        
        new_image_handle = open('./static/face/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
     
        return redirect("/home")

    else:
        return render_template("face.html")    
    
    
if __name__ == '__main__':
      app.run(debug=True)
        
        
                                 
        
       
        
         
         
         
            
 
 
 
 
 



