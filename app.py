from flask import Flask,render_template,request,redirect,url_for
import json
import requests
import pymysql as sql
import pandas as pd
import csv

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup/")
def signup():
    return render_template("signup.html")

@app.route("/login/")
def login():
    return render_template("login.html")

@app.route("/aftersignup/",methods=["POST","GET"])
def aftersignup():
    if request.method == "POST":
        firstname = request.form.get("fname")
        lastname = request.form.get("lname")
        email=request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")
        if password == cpassword:
            try:
                db=sql.connect(host="localhost", port=3306, user="root", password="", database="covidmaster")
            except:
                return "\n Connectivity Issue....."
            else:
                cur =db.cursor()
                cmd = f"select email from user where email='{email}'"
                cur.execute(cmd)
                data = cur.fetchone()
                if data:
                    error = "Email already registered"
                    return render_template("signup.html")
                else:
                    cmd = f"insert into user value('{firstname}','{lastname}','{email}','{password}')"
                    cur.execute(cmd)
                    db.commit()
                    return render_template("login.html")
        else:
            error = "Password does not match please try again"
            return render_template("signup.html", error=error)

    else:
        return render_template("signup.html")


@app.route("/afterlogin/",methods=["POST","GET"])
def afterlogin():
    if request.method == "POST":
        email=request.form.get("email")
        password = request.form.get("password")
        try:
            db = sql.connect(host="localhost", port=3306, user="root", password="", database="covidmaster")
        except Exception as e:
            return e
        else:
            cmd = f"select * from user where email='{email}'"
            cur = db.cursor()
            cur.execute(cmd)
            data = cur.fetchone()
            if data:
                if password == data[3]:
                    print(password)
                    return render_template("afterloginindex.html")
                else:
                    error="Invalid Password...."
                    return render_template("login.html",error=error)
            else:
                error="Invalid Email...."
                return render_template("login.html",error=error)
    else:
        error="Invalid Request...."
        return render_template('login.html',error=error)  

@app.route("/signout/")
def signout():
    return render_template("index.html") 

@app.route("/knowlivestats/")
def livestats():
    url = "https://disease.sh/v2/countries/India"
    content= requests.get(url)
    d = content.json()
    return render_template("livestats.html",data=d)

@app.route("/getdata/", methods=["POST","GET"])
def getdata():
    if request.method=="POST":
        state=request.form.get("state")
        url='https://corona.lmao.ninja/v2/gov/India'
        response=requests.get(url)
        if response.status_code==200:
            page=json.loads(response.text)
            st=page['states']
            d={}
            for i in range(len(st)):
                if st[i]['state']==state:
                    d['total']=st[i]['total']
                    d['recovered']=st[i]['recovered']
                    d['deaths']=st[i]['deaths']
                    d['active']=st[i]['active']
                    return render_template("showdata.html", data=d, state=state)
            else:
                return render_template("livestats.html", error="Invalid state")
        else:
            return render_template("livestats.html", error="Invalid status")
    else:
        return redirect(url_for('login'))

@app.route("/worldlivestats/")
def worldstats():
    url = "https://corona.lmao.ninja/v2/all"
    content= requests.get(url)
    w = content.json()
    return render_template("worldstats.html",data=w)

@app.route("/districtstats/")
def district():
    return render_template("district.html")

@app.route("/disttable/", methods=['POST','GET'])
def dist():
    if request.method == "POST":
        district = request.form.get("district")
        dataDistrict = pd.read_csv("https://api.covid19india.org/csv/latest/district_wise.csv")
        distCases=[]
        for i in range(1, 763):
            if dataDistrict["District"][i] == district:
                districtInfo = [dataDistrict["District"][i], dataDistrict["Confirmed"][i], dataDistrict["Active"][i], dataDistrict["Recovered"][i], dataDistrict["Deceased"][i]]
                distCases.append(districtInfo)
    return render_template("district.html", data=distCases)

@app.route("/statetable/", methods=['POST','GET'])
def state():
    dataState = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise.csv")
    stateCases = []
    total = {}
    total[dataState["State"][0]]= dataState["Active"][0]
    for i in range(1, 38):
        temp = [dataState["State"][i], dataState["Confirmed"][i], dataState["Active"][i], dataState["Recovered"][i], dataState["Deaths"][i]]
        stateCases.append(temp)
    return render_template("statetable.html", data=stateCases, total=total)


    

   

app.run(host="localhost", port=80, debug=True)