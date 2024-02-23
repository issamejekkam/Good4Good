from flask import Flask, render_template, request,redirect,url_for,session,flash
import os
import sqlite3
from flask_mail import Mail,Message
from random import *
from datetime import datetime
import bcrypt





app = Flask(__name__)
app.secret_key = '2023PROJECT2024' 
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'good4ourgood@gmail.com'
app.config['MAIL_PASSWORD'] = "tosd mueh efuf cqok"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
@app.route('/home/')
def home():
    if 'mail' in session:
        mail=session['mail']
        user_data=get_data_by_login(mail)
        return render_template('acceuil.html',user_data=user_data)
    else:
        return render_template('accueil_without_session.html')




@app.route("/login/", methods=["GET","POST"])
def login():
    if request.method=='GET':
        return render_template('login.html')
    if request.method == "POST":
        mail = request.form.get("mail")
        passwordFromSubmit = request.form.get("password")
        con = sqlite3.connect('DB_G4G.db')
        cur = con.cursor()
        cur.execute("SELECT password FROM users WHERE mail=?", (mail,))
        passwordFromBd = cur.fetchone()
        con.close()
        if passwordFromBd and bcrypt.checkpw(passwordFromSubmit.encode('utf-8'), passwordFromBd[0]):
            session['mail'] = mail
            session.permanent=False
            return redirect(url_for('home'))     
        elif passwordFromBd and passwordFromSubmit != passwordFromBd[0]:
            flash("Mot de passe incorrect !")
            return redirect(url_for('login'))
        else: 
            flash("Émail incorrect !")
            return redirect(url_for('login'))
    return redirect(url_for('login'))



@app.route("/sign-up", methods=["GET"])
def showSignUpForm():
    return render_template("sign-up.html")

@app.route("/sign-up", methods=["POST"])
def signUp():
    if request.method == "POST":
        salt = bcrypt.gensalt()
        mail = request.form.get("mail")
        user_name = request.form.get("user_name")
        last_name = request.form.get("last_name")
        first_name = request.form.get("first_name")
        birth_date = request.form.get("birth_date")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        con = sqlite3.connect('DB_G4G.db')
        cur = con.cursor()
        cur.execute("select mail from users")
        result=cur.fetchall()
        if (mail,) in result:
            return render_template('emailutilisé.html')
        cur.execute("INSERT INTO users (mail, user_name, last_name, first_name, birth_date, phone_number, password,points,picture) VALUES ( ?, ?, ?, ?, ?, ?, ?,?,?)", (mail, user_name, last_name, first_name, birth_date, phone_number, hashed_password,"0","none.jpg"))
        con.commit()
        con.close()
        folder_path = os.path.join(app.static_folder, mail)
        os.makedirs(folder_path, exist_ok=True)
        return redirect(url_for('login'))  
    else:
        return "Method not allowed"
    

@app.route("/ForgottenPassword", methods=['GET'])
def resetForm():
    return render_template('ForgottenPAssword.html')





@app.route("/ForgottenPassword", methods=['GET', 'POST'])
def reset():
    if request.method == "POST":
        user_mail = request.form.get("mail")  
        con = sqlite3.connect('DB_G4G.db')
        cur = con.cursor()
        cur.execute('select mail from users where mail=?', (user_mail,))
        fetched_mail = cur.fetchone()

        if fetched_mail:
            otp = str(randint(100000, 999999))
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(otp.encode('utf-8'), salt)
            cur.execute('update users set password=? where mail=?', (hashed_password, fetched_mail[0]))
            con.commit()

            msg = Message(subject='Password Reset OTP', sender='good4ourgood@gmail.com', recipients=[user_mail])
            msg.body = f'Your new password is: {otp}'
            mail.send(msg)  
            return render_template('ResetPasswordrequestSent.html')
    flash('Email inexistant !',"error")
    return render_template('ForgottenPassword.html')  


def get_data_by_login(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE mail = ?;', (mail,))
    user_data = cur.fetchone()
    return user_data

def mail_exists(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('SELECT COUNT(*) FROM users WHERE mail = ?;', (mail,))
    count = cur.fetchone()[0]
    return count > 0

def update_info(info, mail, new_value):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute(f'UPDATE users SET {info} = ? WHERE mail = ?;', (new_value, mail))
    con.commit()
    
def update_info2(info, mail, date_time, new_value):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute(f'UPDATE posts SET {info} = ? WHERE mail = ? AND datetime = ?;', (new_value, mail, date_time))
    con.commit()
    
def update_info3(mail, date_time):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('INSERT INTO posts(mail, datetime) VALUES (?, ?);', (mail, date_time))
    con.commit()

def get_posts_by_login(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM posts WHERE mail = ? ORDER BY datetime DESC;', (mail,))
    user_posts = cur.fetchall()
    return user_posts

def appartenir_associations(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('SELECT association_id FROM appartenir_associations WHERE mail = ?;', (mail,))
    association_ids = cur.fetchall()
    associations = []
    if association_ids:
        for association_id in association_ids:
            cur.execute('SELECT name FROM associations WHERE association_id = ?;', (association_id[0],))
            association_name = cur.fetchone()
            if association_name:
                associations.append(association_name[0])
        con.close()
        return associations
    con.close()
    return ["Pas d'association suivie"]

def delete_post_data(mail, datetime):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('DELETE FROM posts WHERE mail = ? AND datetime = ?;', (mail,datetime))
    con.commit()
    con.close()
def is_post_liked(mail, datetime, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()  
    cur.execute('SELECT * FROM likes WHERE mail = ? AND datetime = ? AND mail2 = ?;', (mail,datetime,mail2))
    result = cur.fetchone()
    return result is not None
def add_like(mail, datetime):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('UPDATE posts SET likes = likes + 1 WHERE mail = ? AND datetime = ?;', (mail, datetime))
    con.commit()
    con.close()
def i_like(mail, datetime, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('INSERT INTO likes VALUES (?,?,?);', (mail, datetime, mail2))
    con.commit()
    con.close()
def i_dislike(mail, datetime, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('DELETE FROM likes WHERE mail = ? AND datetime = ? AND mail2 = ?;', (mail, datetime, mail2))
    con.commit()
    con.close()
def minus_like(mail, datetime):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('UPDATE posts SET likes = likes - 1 WHERE mail = ? AND datetime = ?;', (mail, datetime))
    con.commit()
    con.close()
def add_point(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('UPDATE users SET points = points + 1 WHERE mail = ? ;', (mail,))
    con.commit()
    con.close()
def minus_point(mail):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('UPDATE users SET points = points - 1 WHERE mail = ? ;', (mail,))
    con.commit()
    con.close()
def supp_points(mail,likes):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute(f'UPDATE users SET points = points - {likes} WHERE mail = ? ;', (mail,))
    con.commit()
    con.close()
def are_friends_exist(mail1, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM friends WHERE mail1 = ? AND mail2 = ?;', (mail1,mail2))
    result = cur.fetchone()
    return result is not None
def add_friend_data(mail1, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('INSERT INTO friends (mail1, mail2) VALUES (?, ?);', (mail1,mail2))
    con.commit()
    con.close()
def delete_friend_data(mail1, mail2):
    con = sqlite3.connect('DB_G4G.db')
    cur = con.cursor()
    cur.execute('DELETE FROM friends WHERE mail1 = ? AND mail2 = ?;', (mail1,mail2))
    con.commit()
    con.close()
@app.route('/infos_persos/', methods=["GET", "POST"])
def infos_persos():
    mail= session.get("mail")
    user_data = get_data_by_login(mail)
    if request.method == "GET":
        return render_template("infos_persos.html",user_data=user_data)
    elif request.method == "POST":
        if "fichier" in request.files :
            fichier = request.files.get('fichier')
            if fichier:
                fichier.save(os.path.join('static/profile_pictures', fichier.filename))
                update_info("picture", mail, fichier.filename)
                flash("Photo de profil bien modifiée !","info")
                return redirect(url_for("infos_persos"))
            else :
                flash("Vous n'avez pas saisi une photo !","error")
                return redirect(url_for("infos_persos")) 
        else :               
            if user_data[0]==request.form["mail"] and user_data[1]==request.form["user_name"] and user_data[2]==request.form["last_name"] and user_data[3]==request.form["first_name"] and user_data[4]==request.form["birth_date"] and user_data[5]==request.form["phone_number"] :
                flash("Vous n'avez pas effectué des modifications !","error")       
                return redirect(url_for("infos_persos"))           
            elif mail_exists(request.form["mail"]) :
                if mail == request.form["mail"] :
                    session["mail2"]=request.form["mail"]
                    session["user_name"]=request.form["user_name"]
                    session["first_name"]=request.form["first_name"]
                    session["last_name"]=request.form["last_name"]
                    session["birth_date"]=request.form["birth_date"]
                    session["phone_number"]=request.form["phone_number"]
                    mail=session["mail"]
                    user_data=get_data_by_login(mail)
                    return redirect(url_for('verification',user_data=user_data))
                else : 
                    flash("Profil non modifié !","error")
                    flash("Email est déjà utilisé !","error")       
                    return redirect(url_for("infos_persos"))             
            else :
                session["mail2"]=request.form["mail"]
                session["user_name"]=request.form["user_name"]
                session["first_name"]=request.form["first_name"]
                session["last_name"]=request.form["last_name"]
                session["birth_date"]=request.form["birth_date"]
                session["phone_number"]=request.form["phone_number"]
                mail=session["mail"]
                user_data=get_data_by_login(mail)
                return redirect(url_for('verification',user_data=user_data))


@app.route('/securité/',methods=['GET','POST'])
def securité():
    if request.method == "GET":
        mail=session["mail"]
        user_data=get_data_by_login(mail)
        return render_template("securité.html",user_data=user_data)
    elif request.method == "POST":
        new_password=request.form["new_password"]
        new_password2=request.form["new_password2"]
        if  new_password == new_password2 :
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

            session['new_password'] = hashed_password
            mail=session["mail"]
            user_data=get_data_by_login(mail)
            return redirect(url_for('verification',user_data=user_data))
        else :
            flash("Les deux mots de passes ne sont pas les mêmes !","error")
            return redirect(url_for("securité")) 

 
@app.route('/verification',  methods=["POST","GET"])
def verification():
    if request.method == "GET":
        mail=session["mail"]
        print(0)
        user_data=get_data_by_login(mail)
        return render_template("verification.html",user_data=user_data)
    elif request.method == "POST":
        mail= session.get("mail")
        user_data = get_data_by_login(mail)
        password=request.form["password"] 
        
        if "new_password" in session:
            if not bcrypt.checkpw(password.encode('utf-8'), user_data[6]):
                session.pop('new_password', None)
                session.pop('new_password2', None)
                flash("Vérification refusée !","error")
                return redirect(url_for("securité")) 
            else :
                new_password = session.get('new_password')
                update_info("password", mail, new_password)
                session.pop('new_password', None)
                session.pop('new_password2', None)
                flash("Mot de passe modifié !","info")
                return redirect(url_for("securité"))         
        elif "mail2" in session :
            if not bcrypt.checkpw(password.encode('utf-8'), user_data[6]):
                session.pop('mail2', None)
                session.pop('user_name', None)
                session.pop('last_name', None)
                session.pop('first_name', None)
                session.pop('birth_date', None)
                session.pop('phone_number', None)
                flash("Vérification refusée !","error")
                return redirect(url_for("infos_persos")) 
            else :
                update_info("mail", mail, session["mail2"])
                update_info("user_name", mail, session["user_name"])
                update_info("first_name", mail, session["first_name"])
                update_info("last_name", mail, session["last_name"])
                update_info("birth_date", mail, session["birth_date"])
                update_info("phone_number", mail, session["phone_number"])
                session["mail"]=session["mail2"]
                session.pop('mail2', None)
                session.pop('user_name', None)
                session.pop('last_name', None)
                session.pop('first_name', None)
                session.pop('birth_date', None)
                session.pop('phone_number', None)
                flash("Informations personnelles modifiées !","info")
                return redirect(url_for("infos_persos")) 



@app.route('/logout/')
def logout():
    session.pop("mail", None)
    return redirect(url_for("login"))


@app.route('/Leaderboard')
def Leaderboard():
    if 'mail' in session:
            
            mail= session.get("mail")
            
            user_data = get_data_by_login(mail)
            

            if request.method=='GET' or request.method=='POST':
                con = sqlite3.connect('DB_G4G.db')
                curseur = con.cursor()
                res = curseur.execute("SELECT user_name,points,picture,mail FROM users ORDER BY points DESC")
                res=res.fetchall()
                con.close()

                valeur_recherchee = mail
                for i, sous_liste in enumerate(res):
                    if valeur_recherchee in sous_liste:
                        indice = i+1
                        break
                    else:
                        indice = None


                return render_template('leaderboard_with_session.html',data=res,long=len(res),user=user_data,classement=indice,user_data=user_data)
    else:
        if request.method=='GET' or request.method=='POST':
            con = sqlite3.connect('DB_G4G.db')
            curseur = con.cursor()
            res = curseur.execute("SELECT user_name,points,picture FROM users ORDER BY points DESC")
            res=res.fetchall()
            con.close()
            return render_template('leaderboard.html',data=res,long=len(res),)


@app.route('/profile/',  methods=["POST","GET"])
def profile():
    if "mail" in session :
        if request.method == "GET" :
            mail = session.get("mail")
            user_data = get_data_by_login(mail)
            associations = appartenir_associations(mail)
            user_posts = get_posts_by_login(mail)
            return render_template("profile.html",user_data=user_data,associations=associations,user_posts=user_posts)
        if request.method == "POST" :
            mail= session.get("mail")
            image = request.files.get('image')
            image.save(os.path.join('static/' + mail, image.filename))

            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_info3(mail, current_datetime)
            update_info2('date', mail, current_datetime, datetime.now().strftime('%Y-%m-%d'))
            update_info2('time', mail, current_datetime, datetime.now().strftime('%H:%M:%S'))
            update_info2('likes', mail, current_datetime, 0)
            update_info2('picture', mail, current_datetime, image.filename)

            if 'status' in request.form :
                status = request.form['status']
                update_info2('status', mail, current_datetime, status)
            if 'localisation' in request.form :
                localisation = request.form['localisation']
                update_info2('localisation', mail, current_datetime, localisation)
            flash('Votre publication est bien publiée !',"info")
            return redirect(url_for('profile'))
                
    else :
        return redirect(url_for("login"))
    
@app.route('/visit_profile/<visit_mail>',  methods=["POST","GET"])
def visit_profile(visit_mail):
    if "mail" in session :
        if request.method == "GET" :
            mail = session.get("mail")
            if visit_mail == mail :
                return redirect(url_for("profile"))
            else :
                user_data = get_data_by_login(visit_mail)
                user_data2=get_data_by_login(mail)
                associations = appartenir_associations(visit_mail)
                user_posts = get_posts_by_login(visit_mail)
                amis = are_friends_exist(mail, visit_mail)
                for i, x in enumerate(user_posts):
                    liked_status = is_post_liked(x[0], x[3], mail)
                    user_posts[i] = x + (liked_status,)
                return render_template("visit_profile.html",user_data=user_data,user_data2=user_data2,associations=associations,user_posts=user_posts,amis=amis)
                
    else :
        return redirect(url_for("login"))
    
@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    mail, datetime, likes = post_id.split('|')
    delete_post_data(mail, datetime)
    supp_points(mail,likes)
    flash("Publication supprimée avec succès !","info")
    return redirect(url_for('profile'))

@app.route('/like_post/<post_id>', methods=['POST'])
def like_post(post_id):
    mail2 = session['mail']
    mail, datetime = post_id.split('|')
    add_like(mail, datetime)
    i_like(mail, datetime, mail2)
    add_point(mail)
    return redirect(url_for('visit_profile',visit_mail=mail))

@app.route('/dislike_post/<post_id>', methods=['POST'])
def dislike_post(post_id):
    mail2 = session['mail']
    mail, datetime = post_id.split('|')
    print(mail,datetime)
    minus_like(mail, datetime)
    i_dislike(mail, datetime, mail2)
    minus_point(mail)
    return redirect(url_for('visit_profile',visit_mail=mail))


@app.route('/add_friend/<visit_mail>', methods=['POST'])
def add_friend(visit_mail):
    mail = session['mail']
    add_friend_data(mail,visit_mail)
    return redirect(url_for('visit_profile',visit_mail=visit_mail))

@app.route('/delete_friend/<visit_mail>', methods=['POST'])
def delete_friend(visit_mail):
    mail = session['mail']
    
    delete_friend_data(mail,visit_mail)
    return redirect(url_for('visit_profile',visit_mail=visit_mail))






@app.route('/friends',methods=['GET','POST'])
def friends():
    if "mail" in session:
        mail1 = session['mail']
        user_data=get_data_by_login(mail1)
        username = request.form.get('nom')
        con = sqlite3.connect('DB_G4G.db')
        cur = con.cursor()
        if request.method == 'GET':
            amis=cur.execute('select u.last_name, u.first_name,points,picture,mail from users as u join friends as f on f.mail2=u.mail where f.mail1=?',(mail1,))
            result_amis=amis.fetchall()
            return render_template('friends.html',amis=result_amis,user_data=user_data)
        elif request.method == 'POST':
            amis=cur.execute('select mail2 from friends where mail1=?',(mail1,))
            result_amis=amis.fetchall()
            res = cur.execute('select mail from users where user_name=?', (username,))
            result = res.fetchall()
            if result:
                RESULTAT=[]
                for i in result:
                    amis=cur.execute('select last_name, first_name,points,picture,mail from users where mail=?',(i[0],))
                    result_amis=amis.fetchall()
 
                    result_amis=list(set(result_amis))
                    RESULTAT.append(result_amis)
                    
                    
                return render_template('friendsfounded.html' ,result=RESULTAT,user_data=user_data)
            else:
                amis=cur.execute('select u.last_name, u.first_name,points,picture,mail from users as u join friends as f on f.mail2=u.mail where f.mail1=?',(mail1,))
                result_amis=amis.fetchall()
                flash("Aucun résultat trouvé !","error")
                return render_template('friends.html',amis=result_amis,user_data=user_data)
    else:
        return redirect(url_for('login'))
    



  

@app.route('/association',methods=['GET'])
def association():
    
    if request.method=='GET':
        con=sqlite3.connect('DB_G4G.db')
        cur=con.cursor()
        res=cur.execute('select association_id,picture,address,phone_number,mail,description,name,link from associations order by association_id')
        result=res.fetchall()
        if 'mail'in session:
            mail=session["mail"]
            user_data=get_data_by_login(mail)
            res1=cur.execute('select association_id from appartenir_associations where mail=?',(mail,))
            res1=res1.fetchall()
            result1=[]
            for i in res1:
                result1.append(i[0])





            return render_template('association.html',result=result,result1=result1,user_data=user_data)
        else:
            return render_template('association_hors_session.html',result=result)
@app.route('/suivre_association/<id>',methods=['POST'])
def suivre_association(id):

    if request.method=='POST':
        con=sqlite3.connect('DB_G4G.db')
        cur=con.cursor()
        if 'mail' in session:
            mail=session['mail']

            cur.execute('insert into appartenir_associations values(?,?) ',(id,mail))

            con.commit()
            return redirect(url_for('association'))
        else:
            return redirect(url_for('association'))
@app.route('/ne_pas_suivre_association/<id>',methods=['POST'])       
def ne_pas_suivre_association(id):

    if request.method=='POST':
        con=sqlite3.connect('DB_G4G.db')
        cur=con.cursor()
        if 'mail' in session:
            mail=session['mail']

            cur.execute('delete from appartenir_associations where mail=? and association_id=?',(mail,id))

            con.commit()
            return redirect(url_for('association'))
        else:
            return redirect(url_for('association'))



if __name__ == "__main__":
    app.run(debug=True)

