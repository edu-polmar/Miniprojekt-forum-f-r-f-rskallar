from flask import Flask, session, redirect, url_for, request, render_template
import time as time

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="forum"
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Används för sessionshantering

def get_all_posts():
    cursor = db.cursor()
    cursor.execute("SELECT author, post, time FROM posts ORDER BY time DESC")
    posts = cursor.fetchall()
    cursor.close()
    return posts

@app.route('/')
def index():
    username = session.get('username')  # None om ingen är inloggad

    if username:
        # Anpassat innehåll för inloggad användare
        return f'''
            <h1>Välkommen, {username}!</h1>
            <p>Du är inloggad och behöver inte logga in igen när du klickar runt.</p>
            <ul>
                <button><a href="/profile">Min profil</a></button>
                <button><a href="/posts">Skapa inlägg</a></button>
                <br>
                <button><a href="/logout">Logga ut</a></button>
            </ul>
        '''
    else:
        return '''
            <h1>Inte inloggad</h1>
            <p>Du måste logga in för att se mer.</p>
            <a href="/login">Logga in</a>
            <p>Eller registrera dig:</p>
            <a href="/register">Registrera dig</a>
        '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['passwd']

        # Kolla om användaren finns och lösenordet stämmer
        cursor = db.cursor()
        cursor.execute("SELECT username, passwd FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[1] == password:
            session['username'] = username   # <-- Här skapas sessionen!
            return redirect(url_for('index'))
        else:
            return 'Fel användarnamn eller lösenord. <a href="/login">Försök igen</a>'

    # GET: visa formuläret
    return '''
        <h1>Logga in</h1>
        <form method="post">
            Användarnamn: <input type="text" name="username"><br>
            Lösenord:     <input type="password" name="passwd"><br>
            <input type="submit" value="Logga in">
        </form>
        <p><i>Testa: alice/katt123 eller bob/hund456</i></p>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['passwd']
        name = request.form['name']

        # Kolla om användaren redan finns
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return 'Användarnamnet är redan taget. <a href="/register">Försök igen</a>'

        # Lägg till ny användare i databasen
        cursor.execute("INSERT INTO users (username, passwd, name) VALUES (%s, %s, %s)", (username, password, name))
        db.commit()
        cursor.close()

        return 'Registrering lyckades! <a href="/login">Logga in</a>'

    # GET: visa registreringsformuläret
    return '''
        <h1>Registrera dig</h1>
        <form method="post">
            Användarnamn: <input type="text" name="username"><br>
            Lösenord:     <input type="password" name="passwd"><br>
            Name:         <input type="text" name="name"><br>
            <input type="submit" value="Registrera">
        </form>
    '''

@app.route('/posts', methods=['GET', 'POST'])
def make_posts():
    if 'username' not in session:
        return redirect(url_for('login'))  # Inte inloggad – skicka till login


    if request.method == 'POST':
        post_content = request.form['post']
        timestamp = time.localtime()  # Du kan lägga till en tidsstämpel om du vill
        author = session['username']

        # Spara inlägget i databasen
        cursor = db.cursor()
        cursor.execute("INSERT INTO posts (author, post, time) VALUES (%s, %s, %s)", (author, post_content, timestamp))
        db.commit()
        cursor.close()

        return redirect(url_for('make_posts'))  # Skicka tillbaka till startsidan efter inlägg

    return '''
            <h1>Create post</h1>
            <form method="post">
                Post: <input type="text" name="post"><br>
                <input type="submit" value="Skicka">
            </form>

            <button><a href="/">Tillbaka</a></button>

            <h2>Alla inlägg</h2>
            <ul>
    ''' + ''.join(f'<li><strong>{post[0]}</strong> ({post[2]}): {post[1]}</li>' for post in get_all_posts()) + '''
        '''

@app.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))  # Inte inloggad – skicka till login

    username = session['username']
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    name = user[0] if user else "Namn ej angivet"
    cursor.close()

    return render_template('profile.html', username=username, name=name)

@app.route('/logout')
def logout():
    session.clear()   # Tar bort ALLA sessionsvariabler = utloggad
    return redirect(url_for('index'))


@app.route('/session-info')
def session_info():
    # Visar vad som faktiskt ligger i sessionen
    return f"Session data: {dict(session)}"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 