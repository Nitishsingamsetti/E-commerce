from flask import Flask,render_template,request,flash,redirect,url_for,session
import mysql.connector
from flask_session import Session
from otp import genotp
from stoken import token,dtoken
from cmail import sendmail
import os
app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
mydb=mysql.connector.connect(host='localhost',username='root',password='Raju',db='ecommy')
app.secret_key=b'I|\xbf\x9f'
@app.route('/')
def home():
    return render_template('welcome.html')
@app.route('/index')
def index():
    return render_template('index.html') 
#admin-loginsystem
@app.route('/admincreate',methods=['GET','POST'])
def admincreate():
    if request.method=='POST': 
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        address=request.form['address']
        accept=request.form['agree']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from admincreate where email=%s',[email])
        email_count=cursor.fetchone()[0]
        if email_count==0:
            otp=genotp()
            data={'username':username,'email':email,'password':password,'address':address,'accept':accept,'otp':otp}
            subject='Admin verify for BUYROUTE'
            body=f'Use this otp for verification {otp}'
            sendmail(email=email,subject=subject,body=body)
            flash('OTP has been sent to give mail')
            return redirect(url_for('adminverify',var1=token(data=data)))
        elif email_count==1:
            flash('Email Already existed')
            return redirect(url_for('adminlogin'))
        else:
            return 'something went wrong'    
    return render_template('admincreate.html') 
@app.route('/adminverify/<var1>',methods=['GET','POST'])
def adminverify(var1):
    try:
        regdata=dtoken(data=var1)
    except Exception as e:
        print(e)
        return 'Something went wrong'
    else:
        if request.method=='POST':
            uotp=request.form['otp']
            if uotp==regdata['otp']:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into admincreate(email,username,password,address,accept) values (%s,%s,%s,%s)',[regdata['email'],regdata['username'],regdata['password'],regdata['address'],regdata['accept']])
                mydb.commit()
                cursor.close()
                flash(f"{regdata['email']} Registration successfully Done")
                return redirect(url_for('adminlogin'))
            else:
                return 'Invaild otp'    
    return render_template('adminotp.html')
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        password=password.encode('UTf-8')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from admincreate where email=%s',[email])
        count=cursor.fetchone()
        print(count)
        if count:
            if count[0]==1:
                cursor.execute('select password from admincreate where email=%s',[email])
                dbpassword=cursor.fetchone()
                print(dbpassword)
                if dbpassword:
                    if dbpassword[0]==password:
                        session['email']=email
                        if not session.get(email):
                            session[email]={}
                        return redirect(url_for('adminpanel'))
                    else:
                        flash('wrong password')
                else:
                    flash('invaild input for password')
                    return redirect(url_for('adminlogin'))
            else:
                flash('worng email')
                return redirect(url_for('adminlogin'))
        else:
            flash('invalid input for email.')
            return redirect(url_for('adminlogin'))                    

    return render_template('adminlogin.html')
@app.route('/adminpanel')
def adminpanel():
    return render_template('adminpanel.html') 
@app.route('/additem',methods=['GET','POST'])
def additem():
    if not session.get('email'):
        return redirect(url_for('adminlogin'))
    else:
        if request.method=='POST':
            item_name=request.form['title']
            description=request.form.get('description')
            quantity=request.form['quantity']
            category=request.form['category']
            file=request.files['file']
            price=request.form['price']
            print(request.form)    
            filename=genotp()+'.'+file.filename.split('.')[-1]
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            file.save(os.path.join(static_path,filename))
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into items(item_id,item_name,description,price,quantity,image_name,added_by,category) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s)',[item_name,description,price,quantity,filename,session.get('email'),category])
            mydb.commit()
            cursor.close()
            flash(f'Item {item_name} added successfully')
    return render_template('additem.html') 
@app.route('/adminlogout')
def adminlogout():
    if session.get('email'):
        session.pop(session.get('email'))
        return redirect(url_for('adminlogin'))
    else:
        return redirect(url_for('adminlogin'))              
app.run(debug=True,use_reloader=True)