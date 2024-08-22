from flask import Flask,render_template,url_for,request

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('welcome.html')

app.run(debug=True,use_reloader=True)


