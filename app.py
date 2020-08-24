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
        result = formulae.analyseabg(ph, po2, pco2, hco3, na, cl, age, alb, fio2)
        print(result)
        #return render_template("result.html", list=result)
        return jsonify(result)
if __name__ == '__main__':
    app.run()
