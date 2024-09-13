from flask import Flask,render_template,request,flash,redirect,url_for,session,Response
import mysql.connector
from flask_session import Session
from otp import genotp
from stoken import token,dtoken
from cmail import sendmail
import os
import re
import razorpay
import pdfkit
app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
config=pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
RAZORPAY_KEY_ID='rzp_test_Rxy19zNIFo9p8r'
RAZORPAY_KEY_SECRET='eIHxmEyJqhKzZ10tHEy7Kkkc'
client= razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))
#mydb=mysql.connector.connect(host='localhost',username='root',password='nitish',db='ecommy')
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')

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
    
@app.route('/delete_item')
def delete_item():
    if not session.get('email'):
        render_template(url_for('adminlogin'))
    else:
        cursor=mydb.cursor(buffered=True)
        cursor.execute()

        
        
@app.route('/remove/<itemid>')
def remove(itemid):
    if session.get('useremail'):
        print(session.get('useremail'))
        session[session.get('useremail')].pop(itemid)
        return redirect(url_for('veiwall'))
    return redirect(url_for('userlogin'))

def search():
    if request.method=='POST':
        name=request.form['search']
        strg=['a-zA-Z0-9']
        pattern=re.compile(f'{strg}',re.IGNORECASE)
        query='select bin_to_build(u_id),item_name,description,price,quantity'
        search_pram=f'%{name}%'
        cursor=mydb.cursor(buffered=True)
        cursor.execute(query,{search_pram,search_pram,search_pram,search_pram})
        data=cursor.fetchall()
        return render_template('dashbord.html',items_data=data)
    else:
        flash('result not found')
        
app.route('/contactus',methods=['POST','GET'])
def contactus():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        text=request.form['text']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into contact_us values (%s,%s,%s)',[name,email,text])
        mydb.commit()
        cursor.close()
        return render_template(url_for('contactus'))
    
    
    
    
    return render_template('contact.html')

app.route('/veiwcontact')
def veiwcontact():
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select * from contact_us')
    data=cursor.fetchall()
    return render_template('veiwcontatc.html',items_data=data)

@app.route('/pay/<itemid>/<name>/<int:price',methods=['GET','POST'])
def pay(itemid,name,price):
    try:
        qyt=int(request.form('qyt'))
        amount=price*100    #convert price into price
        total_price = amount * qyt
        print(f'creating payment for item:{itemid},name:{name},price:{price}')
        #create razorpay oredr
        order=client.order.create({
            'amount':amount,
            'currency':'INR',
            'payment_capture':'1'
        })
        print(f'order created: {order}')
        return render_template('pay.html',order=order,itemid=itemid,name=name,price=price)
    except Exception as e :
        return str(e),400
    
@app.route('//success',methods=['POST'])
def success():
    #extract payment details from, the form
    payment_id=request.form.get('razorpay_payment_id')
    order_id=request.form.get('razrpay_order_id')
    signature=request.form.get('razorpay_signature')

    #verification process
    params_dict={'razorpay_payment_id':order_id,'razrpay_order_id':payment_id,'razorpay_signature':signature}
    try:
        client.utility.verify_payment_signature(params_dict)
        return redirect(url_for("orders"))
    except razorpay.errors.SignatureVerificationError:
        return 'payment verification failed',400
@app.route('/orders')
def orders():
    return 'hi'

@app.route('/billdetails/<ordid>.pdf')
def invoice(ordid):
    if session.get('username'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from orders where ordid=%s',[ordid])
        orders=cursor.fetchone()
        username=orders[5]        
        oname=orders[2]        
        qty=orders[3]        
        cost=orders[4]
        cursor.execute('select username,address,user_email from usercreate where user_email=%s',[username])
        data=cursor.fetchone()
        uname=data[0]
        uaddress=data[1]
        html=render_template('bill.html',uname=uname,uaddress=uaddress,oname=oname,qty=qty,cost=cost)
        pdf=pdfkit.from_string(html,False,configuration=config)
        response=Response(pdf,content_type='application/pdf')
        response.headers['content-Disposition']='inline;filename=output.pdf'
        return response
        
               
        
    
    
    
                
app.run(debug=True,use_reloader=True)