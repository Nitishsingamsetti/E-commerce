from flask import Flask,render_template,url_for,request

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/index')
def index():
    return render_template('index.html')

app.route('/admincreate',methods=['GET','POST'])
def admincreate():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        address=request.form['address']
        accept=request.form['agree']
        print(request.form)
    return render_template('admincreate.html')


app.run(debug=True,use_reloader=True)



