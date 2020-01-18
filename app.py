import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
app=Flask(__name__)
app.secret_key = '56fgpknn5kp'

engine = create_engine("postgres://efywljzbctnors:1163807423bed5e3b9e21e470bdab0b4e1721147755110f4b73851df62bb6a29@ec2-176-34-184-174.eu-west-1.compute.amazonaws.com:5432/dapnjtf2ckbqbq")
db = scoped_session(sessionmaker(bind=engine))


#main page
KEY="LMkmCT1hycZRWqvDAZnmJA"
@app.route("/")
def one():
	if 'user' in session:
		return redirect (url_for('search'))
	return render_template ("index.html");
@app.route("/registration")
def registration():
		return render_template ("registration.html");


#registration function
@app.route("/engines", methods=["POST"])
def engines():
	username=request.form.get("username")
	password=request.form.get("pass")
	name=request.form.get("name")
	writer=request.form.get("writer")
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
			return render_template("message.html", message="username already exist")
	db.execute("INSERT INTO users (username, password, name, writer) VALUES (:username, :password, :name, :writer)",
			{"username": username,"password": password, "name": name, "writer": writer})
	db.commit()
	return  render_template("message.html", message="thank you for registering")


#login function
@app.route("/login", methods=["POST"])
def login():
	usernamelog=request.form.get("usernamelog")
	passlog=request.form.get("passlog")
	if db.execute("SELECT * FROM users WHERE username= :usernamelog AND password= :passlog",
	 {"usernamelog": usernamelog, "passlog": passlog}).rowcount == 1:
		session['user']=usernamelog
		return redirect (url_for("search"))
	else:
		return render_template("message.html", message="incorrect username or password")


#search function and page
@app.route("/search", methods=["POST", "GET"])
def search():
	if 'user' in session: 
		nn=db.execute("SELECT name FROM users WHERE username=:username", {"username":session['user']}).fetchone()
		return render_template('search.html', nn=nn.name)
	return render_template("message.html", message="please log in")


#drop sesion and redirect to main page
@app.route("/logout", methods=["POST"])
def logout():
	session.pop('user', None)
	return redirect (url_for("one"))


#Searchresult page
@app.route("/result", methods=["POST"])
def result():
	result=request.form.get("wordrequest")
	result='%'+result+'%'
	
	if db.execute("SELECT * FROM books WHERE author LIKE :author OR isbn LIKE :isbn OR title LIKE :title", {"author":result,
	 "title":result, "isbn":result}).rowcount==0:
		return render_template("message.html", message="there is no such result")
	booksres=db.execute("SELECT * FROM books WHERE author LIKE :author OR isbn LIKE :isbn OR title LIKE :title", {"author":result,
	 "title":result, "isbn":result}).fetchall()
	return render_template("result.html", booksres=booksres)


#book page
@app.route("/book/<isbn>")
def book(isbn):
	bookbook=db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	reviews5=db.execute("SELECT * FROM reviews WHERE isbn=:isbn LIMIT 5", {"isbn":isbn}).fetchall()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
	data=res.json()
	rate=data["books"][0]["average_rating"]
	count=data["books"][0]["work_ratings_count"]
	return render_template("book.html", bookbook=bookbook, reviews5=reviews5, rate=rate, count=count)


#write review function
@app.route("/review/<isbn>")
def review(isbn):
	comment=request.args.get("review")
	rate=request.args.get("rate", type=int)
	user=session["user"]
	if db.execute("SELECT*FROM reviews WHERE isbn=:isbn AND users=:users", {"isbn":isbn, "users":user}).rowcount>0:
		return render_template("message.html", message="Sorry you cant comment book twice")
	db.execute("INSERT INTO reviews (isbn, users, comment, rating) VALUES (:isbn, :users, :comment, :rating)",
        {"isbn": isbn,"users": user, "comment": comment, "rating": rate})
	db.commit()
	return render_template("message.html", message="thank you for comment")
x=()



#api function
@app.route("/api/<isbn>")
def api(isbn):
	bookss=db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	if bookss is None:
		return jsonify({"error":"isbn doesnt exist in our database"}), 404
	booksrew=db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	review_count=db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).rowcount
	average_score=db.execute("SELECT AVG(rating) FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	for column, value in average_score.items():
		x = value
		z=float(x)
	return jsonify({
		"title": bookss.title,
		"author": bookss.author,
		"year": bookss.year,
		"isbn": isbn,
		"review_count": review_count,
		"average_score": z
		})


