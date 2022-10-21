from flask import Flask, flash, render_template, request
import pandas as pd
import pickle
from joblib import dump, load
import warnings

# Ignorar los warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "clave"

_classnames = ['NO','SI']

@app.route("/")
def prueba():
    return render_template("index.html")


@app.route("/", methods = ['POST'])
def inicio():
    if request.method == "POST":
        # Lee los valores de las cajas de texto de la interfaz
        age = float(request.form['age'])
        job = str(request.form['job'])
        marital = str(request.form['marital'])
        education = str(request.form['education'])
        default = str(request.form['default'])
        balance = float(request.form['balance'])
        housing = str(request.form['housing'])
        loan = str(request.form['loan'])
        contact = str(request.form['contact'])
        day = float(request.form['day'])
        month = str(request.form['month'])
        duration = float(request.form['duration'])
        campaign = float(request.form['campaign'])
        pdays = float(request.form['pdays'])
        previous = float(request.form['previous'])
        poutcome = str(request.form['poutcome'])


        X = [[age,	job,	marital,	education,	default,	balance,	housing,	loan,	contact,	day,	month,	duration,	campaign,	pdays,	previous,	poutcome]]
        df_X = pd.DataFrame(X)
        df_X.columns = ['age', 'job', 'marital', 'education', 'default', 'balance', 'housing', 'loan', 'contact', 'day', 'month', 'duration', 'campaign', 'pdays','previous', 'poutcome']

        model = pickle.load(open('modelo_lr.pickle','rb'))
        result = _classnames[model.predict(df_X)[0]]

    else:
        result = ""
    return render_template("index.html", result = result)   


if __name__ == '__main__':
    app.run(port=5000, debug= True)  

################################################################################


# import pickle # pylint: disable=import-error
# import warnings
# warnings.filterwarnings("ignore")

# from flask import Flask, flash, render_template, request

# app = Flask(__name__)
# app.config["SECRET_KEY"] = "you-will-never-guess"

# # Nombres de las clases
# classnames = ["setosa", "versicolor", "virginica"]


# @app.route("/", methods=["GET", "POST"])
# @app.route("/index", methods=("GET", "POST"))
# def index():

#     if request.method == "POST":

#         # Lee los valores de las cajas de texto de la interfaz
#         sepal_length = float(request.form["sepal_length"])
#         sepal_width = float(request.form["sepal_width"])
#         petal_length = float(request.form["petal_length"])
#         petal_width = float(request.form["petal_width"])

#         X = [[sepal_length, sepal_width, petal_length, petal_width]]
        

#         # Loading model from disk
#         model = pickle.load(open('model.pkl','rb'))
#         result = classnames[model.predict(X)[0]]
#     else:
#         result = ""

#     return render_template("index.html", result=result)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True)