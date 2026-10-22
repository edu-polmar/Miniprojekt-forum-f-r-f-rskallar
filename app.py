from flask import Flask, session, redirect, url_for, request

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="forum"
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Används för sessionshantering




@app.route('/')
def index():
    username = session.get('username')  # None om ingen är inloggad

    if username:
        # Anpassat innehåll för inloggad användare
        cursor = db.cursor()
        cursor.close()
        return f'''
            <h1>Välkommen, {username}!</h1>
            <p>Du är inloggad och behöver inte logga in igen när du klickar runt.</p>
            <ul>
                <li><a href="/profile">Min profil</a></li>
                <li><a href="/secret">Hemlig sida (kräver inloggning)</a></li>
                <li><a href="/logout">Logga ut</a></li>
            </ul>
        '''
    else:
        return '''
            <h1>Inte inloggad</h1>
            <p>Du måste logga in för att se mer.</p>
            <a href="/login">Logga in</a>
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


@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Inte inloggad – skicka till login

    return f'''
        <h1>Profil för {username}</h1>
        <p><a href="/">Tillbaka</a></p>
    '''


@app.route('/secret')
def secret():
    # Exempel på en skyddad sida
    if 'username' not in session:
        return redirect(url_for('login'))

    return f'''
        <h1>🔒 Hemlig sida</h1>
        <p>Bara {session['username']} kan se detta.</p>
        <p><a href="/">Tillbaka</a></p>
    '''


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