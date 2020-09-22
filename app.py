from flask import Flask, render_template, request, jsonify
import formulae

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=["GET", "POST"])
def result():
    if request.method == "POST":
        age = float(request.form['age'])
        ph = float(request.form['ph'])
        po2 = float(request.form['po2'])
        pco2 = float(request.form['pco2'])
        hco3 = float(request.form['hco3'])
        na = float(request.form['na'])
        cl = float(request.form['cl'])
        alb = float(request.form['alb'])
        fio2 = float(request.form['fio2'])
        result = formulae.analyseabg(ph=ph, po2=po2, pco2=pco2, hco3=hco3, na=na, cl=cl, age=age, albumin=alb, fio2=fio2)
        print(result)
        #return render_template("result.html", list=result)
        try:
            counter =  open("count.txt", "r")
            data = counter.readline()
            intdata = int(data)
            intdata += 1
            data = str(intdata)
            counter = open("count.txt", "w")
            counter.writelines(data)
        except:
            print("counter read/write exception")
        return jsonify(result)
@app.route('/fio2', methods=["GET", "POST"])
def fio2():
    if request.method == "POST":
        o2flowrate = float(request.form['o2flow'])
        deliverytype = float(request.form['device'])
        colorcode = int(request.form['colorcode'])
        result2 = formulae.getfio2(o2flowrate, deliverytype, colorcode)
        print(result2)
        return jsonify(result2)

@app.route('/visitor_count_3.1416', methods=["GET"])
def getvisitors():
    try:
        counter =  open("count.txt", "r+")
        data = counter.readline()
        intdata = int(data)
        return "<p>Number of visitors so far: " + str(intdata) + "</p>"
    except:
        return("counter read/write exception")
if __name__ == '__main__':
    app.run()
