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
    return render_template('admincreate.html')


app.run(debug=True,use_reloader=True)



