import os
import secrets
from PIL import Image
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_wtf.file import FileField, FileAllowed
from cs50 import SQL
from flask_session import Session


app = Flask(__name__)

db = SQL("sqlite:///customers.db")

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)



def save_picture_items(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_it = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/items_img', picture_it)
    output_size = (720, 1080)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_it



def save_picture_users(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_pr = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_img', picture_pr)
    output_size = (720, 720)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_pr



def save_picture_pets(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_pt = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pets_img', picture_pt)
    output_size = (720, 720)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_pt

def save_cv(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_cv = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/cv', picture_cv)
    i = open(form_picture)
    i.save(picture_path)

    return picture_cv



@app.route('/')
def index():
    if session.get("user_id",None):
        user_name = db.execute("SELECT * FROM customers WHERE id=?", session['user_id'])
        return render_template("index.html",user_name=user_name)
    
    return render_template("index.html")

@app.route('/sign_up', methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        if session.get("user_id",None):
            return redirect("/")
        return render_template("sign-up.html")

    if request.method == 'POST':

        fullname = request.form.get("fullname",None)
        username = request.form.get("username",None)
        email = request.form.get("email",None)
        password = request.form.get("password",None)
        phone_number = request.form.get("phone",None)
        address = request.form.get("address",None)
        form_picture = request.files["pic"]
        user_pic = save_picture_users(form_picture)
        # user_pic = save_picture_users(request.form.get("member_pic",None))
        if not fullname or not email or not password or not username or not phone_number or not address:
            # flash("Please complete your information","danger")
            return redirect("/sign_up")
        rowss = db.execute("INSERT INTO customers(fullname,username,email,password,phone,address,pic)VALUES(?,?,?,?,?,?,?)",fullname,username,email,password,phone_number,address,user_pic)
        session['user_id'] = rowss
        # flash("welcome","success")
        return redirect("/")
    if session.get("user_id",None):
        # return redirect("/")
        return redirect("/")
    




        
    



@app.route('/log_in',methods=['GET','POST'])
def login():
    

    if request.method == 'POST':
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if not email or not password:
            # flash("email or password not correct","danger")
            return redirect("/login")

        rows = db.execute("SELECT * FROM customers where email= ?",email)
        if len(rows) < 1:
            return redirect("/register")
            
        if not password == rows[0]['password']:
            # flash("email or password not correct","danger")
            return redirect("/login")


        session['user_id'] = rows[0]['id']
        return redirect("/")
    if session.get("user_id",None):
        return redirect("/")
    return render_template("log-in.html")

@app.route('/log_out', methods=['GET','POST'])
def log_out():
    if not session.get("user_id",None):
        return redirect("/sign_up")
    del session['user_id']
    return redirect("/")





@app.route('/payment_cart',methods=['GET','POST'])
def payment():
    if not session.get("user_id",None):
        return render_template("index.html")
    

    if session.get("user_id",None):
        cart_items = db.execute("SELECT * FROM cart WHERE user_id = ?", session.get("user_id"))


        return render_template("payment.html",cart_items=cart_items)

@app.route('/del_item',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        id_it = request.form.get("it_id",None)
        id_us = session['user_id']
        db.execute("DELETE FROM cart WHERE user_id=? AND items_id=?",id_us,id_it)
        return redirect("/payment_cart")
    return redirect("/payment_cart")

    
    



@app.route('/store', methods=['GET','POST'])
def store():
    if request.method == 'POST':
        id_user = request.form.get("id_user",None)
        id_item = request.form.get("id_item",None)
        name_item = request.form.get("item_name",None)
        photo_item = request.form.get("item_photo",None)
        price_item = request.form.get("item_price",None)
        db.execute("INSERT INTO cart(user_id,items_id,name,photo,price)VALUES(?,?,?,?,?)",id_user,id_item,name_item,photo_item,price_item)
        return redirect("/store")

    if not session.get("user_id",None):
        items = db.execute("SELECT * FROM items")
        return render_template("store.html",items=items)
    if session.get("user_id",None):
        user_name = db.execute("SELECT * FROM customers WHERE id=?", session['user_id'])
        items = db.execute("SELECT * FROM items")

        return render_template("store.html",items=items,user_name=user_name)

    


@app.route('/adoption',methods=['GET','POST'])
def adoption():
    if not session.get("user_id",None):
        pets = db.execute("SELECT * FROM pets")
        return render_template("adopting.html",pets=pets)

    if session.get("user_id",None):
        pets = db.execute("SELECT * FROM pets")
        user_name = db.execute("SELECT * FROM customers WHERE id=?", session['user_id'])

        return render_template("adopting.html",user_name=user_name,pets=pets)


@app.route('/promote_pet',methods=['GET','POST'])
def promote():
    if request.method == 'POST':
        pet_name = request.form.get("name", None)
        pet_age = request.form.get("age", None)
        pet_kind = request.form.get("kind", None)
        pet_governorate = request.form.get("governorate", None)
        form_picture = request.files["photo"]
        pet_pic = save_picture_pets(form_picture)
        pet_condition = request.form.get("message", None)
        pet_gender = request.form.get("gender", None)
        pet_vaccination =request.form.get("vaccine", None)
        if not pet_name or not pet_age or not pet_kind or not pet_governorate or not pet_gender or not pet_vaccination or not pet_pic:
            #     flash("please complete the information","danger")
            return redirect("/promote_pet")
        db.execute("INSERT INTO pets(name,age,kind,governorate,condition,gender,vaccinated,photo)VALUES(?,?,?,?,?,?,?,?)",pet_name,pet_age,pet_kind,pet_governorate,pet_condition,pet_gender,pet_vaccination,pet_pic)
            # flash("pet promoted successfully","success")
        return redirect("/adoption")
    return render_template("pet-info.html")



@app.route('/profile',methods=['GET','POST'])
def profile():
    if not session.get("user_id",None):
        return render_template("sign.html")
    
    customers = db.execute("SELECT * FROM customers WHERE id=?", session.get('user_id'))
    
    return render_template("profile.html",customers=customers)

@app.route('/contact_us',methods=['GET','POST'])
def contact():

    if request.method == 'POST':
        
        if session['user_id'] == None:
            name = request.form.get("name", None)
            email = request.form.get("email", None)
            subject = request.form.get("subject", None)
            message = request.form.get("message", None)

            if not name or not email or not subject or not message:
                # flash("please complete the form","danger")
                return redirect("/contact_us")

            db.execute("INSERT INTO messages(fullname,email,subject,message)VALUES(?,?,?,?)",name,email,subject,message)
            return render_template("index.html")
        id = session['user_id']
        name = request.form.get("name", None)
        email = request.form.get("email", None)
        subject = request.form.get("subject", None)
        message = request.form.get("message", None)

        if not name or not email or not subject or not message:
            # flash("please complete the form","danger")
            return redirect("/contact_us")

        db.execute("INSERT INTO messages(id,fullname,email,subject,message)VALUES(?,?,?,?,?)",id,name,email,subject,message)
        return render_template("index.html")

    return render_template("get in touch.html")        
    
    

    


@app.route('/admin', methods=['GET','POST'])
def admin():
        
    if request.method == 'POST':
        name = request.form.get("name", None)
        animal_kind = request.form.get("animal", None)
        price = request.form.get("price", None)
        quantity = request.form.get("quantity", None)
        description = request.form.get("description", None)
        form_picture = request.files["pic"]
        photo = save_picture_items(form_picture)

        db.execute("INSERT INTO items(name,animal_kind,price,quantity,description,photo)VALUES(?,?,?,?,?,?)",name,animal_kind,price,quantity,description,photo)
        return redirect("/store")

    if session['user_id']:
        return render_template("admin.html")    
    




@app.route('/services')
def services():
    if session.get("user_id",None):
        user_name = db.execute("SELECT * FROM customers WHERE id=?", session['user_id'])
        service = db.execute("SELECT * FROM workers")
        return render_template("services.html",service=service,user_name=user_name)

    service = db.execute("SELECT * FROM workers")
    return render_template("services.html",service=service)


@app.route('/work_with_us', methods=['GET','POST'])
def wwu():
    if request.method == 'GET':
        return render_template("work with us.html")
    if request.method == 'POST':
        id = session['user_id']
        name = request.form.get("name", None)
        email = request.form.get("email", None)
        address = request.form.get("address", None)
        phone = request.form.get("phone", None)
        profession = request.form.get("profession", None)
        # form_picture = request.files["cv"]
        # cv = save_cv(form_picture)
        message = request.form.get("message",None)
        if not name or not email or not address or not phone or not profession or not message:
            return redirect("/work_with_us")
        db.execute("INSERT INTO requests(id,name,email,address,phone,profession,message)VALUES(?,?,?,?,?,?,?)",id,name,email,address,phone,profession,message)
        return redirect("/")
    # return render_template("work with us.html")












if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, Debug=True)