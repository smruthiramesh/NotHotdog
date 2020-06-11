from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from getrecipes import getrecipes

app = Flask(__name__)


app.config['MYSQL_USER	'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Fibonacci96'
app.config['MYSQL_DB'] = 'recipes'

mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT title,url,img FROM cookie_kate ORDER BY rating LIMIT 5''')
    results = cur.fetchall()
    return render_template('newdrop.html', data=results)

@app.route('/recipe',methods=['GET'])
def result():
    if request.method == 'GET':
        cuisine = request.args.get("cuisine")
        category = request.args.get("category")
        rating = float(request.args.get("rating"))
        cooktime = tuple([int(k) for k in request.args.get("cooktime").split(',')])
        ingredients = request.args.get("ing")
        subset = getrecipes(cuisine,category,cooktime,rating,ingredients)[["title","url","img"]]
        results = [tuple(x) for x in subset.to_numpy()]
        return render_template('newdrop.html', data=results)

if __name__ == "__main__":
    app.run(debug=True)
