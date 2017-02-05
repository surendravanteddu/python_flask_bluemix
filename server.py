import os
import swiftclient
import keystoneclient
import pyDes
import mysql.connector
from flask import Flask, request, render_template

app = Flask(__name__)
k = pyDes.des(b"DESCRYPT", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
auth_url = "https://identity.open.softlayer.com/v3"
password = "HWr6BhP)i1vlC]cg"
project_id = "97fecd12d55c42b381e8dc72e7621f3d"
user_id = "68aa86b5112d4cc299f4361e01953f75"
region_name = 'dallas'
conn = 	swiftclient.Connection (key=password, 
                                authurl=auth_url,
                                auth_version='3',
                                os_options={"project_id" : project_id,
                                            "user_id" : user_id, 
                                            "region_name" : region_name})


conn.put_container("Hola")

@app.route('/')
def Welcome():
    return render_template('nav.html')

@app.route('/addData')
def Welcome1():
    return render_template('first.html')

@app.route('/login')
def Welcome2():
    return render_template('login.html')
@app.route('/home')
def Welcome3():
    return render_template('home.html')

@app.route('/insert',methods=['POST'])
def insertId():
    if request.method == 'POST':
      try:     
       
       cursor = cnx.cursor()        
       cursor.execute("insert into users (id,password) values ('"+request.form['name']+"','"+request.form['password']+"')")
       results = cursor.fetchone()
       # Check if anything at all is returned
       if results:
          print "connected"
       else:
          print "failed"
       cnx.commit()

       cursor.close()
       #cnx.close()    
      except MySQLdb.Error:
       print "ERROR IN CONNECTION"       
    return "inserted"   

@app.route('/logincheck',methods=['POST'])
def logincheck():
    if request.method == 'POST':
      try:     
       cnx = mysql.connector.connect(user='bacac3db00c1af', password='f270bef8',
                              host='us-cdbr-iron-east-04.cleardb.net',
                              database='ad_6b84625cabb4617')
       cursor = cnx.cursor()        
       cursor.execute("select id from users where id = '"+request.form['name']+"' and password='"+request.form['password']+"'")
       result = "failed"
       for (id) in cursor:
         print("{}".format(id))
         result = "success"
            
       cnx.commit()

       cursor.close()
       cnx.close()    
      except MySQLdb.Error:
       print "ERROR IN CONNECTION"       
    if result == "success":
       return "<html><body><p>welcome "+request.form['name']+",</p><br/><a href=\"home\">Add file</a></body></html>"
    else:
       return "<html><body><p>Login failed</p></body></html>"    
      
@app.route('/uploadfile',methods=['GET','POST'])
def uploadfile():
    if request.method == 'POST':
        file = request.files['file_upload']
        filename = file.filename
        content=file.read()
        try:     
         cnx = mysql.connector.connect(user='bacac3db00c1af', password='f270bef8',
                              host='us-cdbr-iron-east-04.cleardb.net',
                              database='ad_6b84625cabb4617')
         cursor = cnx.cursor()        
         cursor.execute("insert into userfiles (id,description,filename,ufile) values ('"+request.form['name']+"','"+request.form['description']+"','"+filename+"','"+content+"')")
         result = "success"
         
         cnx.commit()

         cursor.close()
         cnx.close()    
        except MySQLdb.Error:
         print "ERROR IN CONNECTION"
    return result       
        
@app.route('/upload',methods=['GET','POST'])
def Upload():
  if request.method=='POST':
    file= request.files['file_upload']
    filename=file.filename
    content=file.read()
    #encryptContent = content.encode('UTF-8')
    
    encryptedD = k.encrypt(content)
    conn.put_object("Hola", 
		filename, 
		contents = encryptedD, 
		content_type="text")
    
    return '<h1>Awesome! Files uploaded.<h1><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/download',methods=['GET','POST'])
def Download():
    if request.method=='POST':
      filename = request.form['file_download']
      file = conn.get_object("Hola",filename)
      fileContentsBytes = file[1]#str(file)
      #fileContents = k.decrypt(fileContentsBytes).decode('UTF-8')
      #for x in file:
       # fileContents = fileContents + x
        #for y in file[x]:
         # fileContents = "<br>" + fileContents + "<br>"
          

      return '<h3>The File is,</h3><br><br>' + fileContentsBytes + '<br><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/delete',methods=['GET','POST'])
def Delete():
    if request.method=='POST':
      filename = request.form['file_delete']
      file = conn.delete_object("test_container",filename)

      return '<h3>The File has been successfully deleted,</h3><br><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/list')
def List():
  listOfFiles = ""
  for container in conn.get_account()[1]:
    for data in conn.get_container(container['name'])[1]:
      if not data:
        listOfFiles = listOfFiles + "<i> No files are currently present on Cloud.</i>"
      else:
        listOfFiles = listOfFiles + "<li>" + 'File: {0}\t Size: {1}\t Date: {2}'.format(data['name'], data['bytes'], data['last_modified']) + "</li><br>"
  return '<h3>The files currently on cloud are </h3><br><br><ol>' + listOfFiles + '<br><form action="../"><input type="Submit" value="Lets go back"></form>'

if __name__ == "__main__":
    app.run(debug=True)