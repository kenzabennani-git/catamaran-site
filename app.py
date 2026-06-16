from catamaran_loisir import CatamaranLoisir
from catamaran_sportif import CatamaranSportif

from flask import Flask, render_template, request, redirect, flash, url_for, session
from db_config import get_db_connection
from mysql.connector import Error
import random
from functools import wraps


app = Flask(__name__)
app.secret_key = "cle_super_secrete"


def recuperer_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vous devez être connecté pour accéder à cette page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vous devez être connecté.", "error")
            return redirect(url_for("login"))

        if session.get("user_role") != "admin":
            flash("Accès refusé.", "error")
            return redirect(url_for("accueil"))

        return f(*args, **kwargs)
    return decorated_function


def recuperer_mes_reservations(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM inscriptions
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations


def recuperer_toutes_reservations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM inscriptions
        ORDER BY created_at DESC
    """)
    reservations = cursor.fetchall()
    conn.close()
    return reservations


def compter_utilisateurs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def compter_reservations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inscriptions")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def calculer_places_prises_par_nom(nom_evenement):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT COALESCE(SUM(nombre_places), 0) AS total
        FROM inscriptions
        WHERE evenement = %s
    """, (nom_evenement,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat["total"] if resultat else 0


def mettre_a_jour_places_prises_par_nom(nom_evenement):
    total = calculer_places_prises_par_nom(nom_evenement)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE evenements
        SET places_prises = %s
        WHERE nom = %s
    """, (total, nom_evenement))
    conn.commit()
    conn.close()


# ==============================
# LECTURE DES DONNÉES DEPUIS LA BDD
# ==============================

def recuperer_catamaran(id_catamaran):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM catamaran WHERE id_catamaran = %s", (id_catamaran,))
    cat = cursor.fetchone()

    if not cat:
        conn.close()
        return None

    if cat["type_catamaran"] == "Loisir":
        cursor.execute(
            "SELECT * FROM catamaranloisir WHERE id_catamaran = %s",
            (id_catamaran,)
        )
        loisir = cursor.fetchone()
        conn.close()

        return CatamaranLoisir(
            cat["id_catamaran"],
            cat["nom"],
            cat["type_catamaran"],
            cat["longueur"],
            cat["largeur"],
            cat["hauteur"],
            cat["tirant_eau"],
            cat["vitesse_noeud"],
            cat["capacite"],
            cat["categorie_type_B"],
            loisir["voile_loisir"],
            loisir["coque_rotomoule"]
        )

    if cat["type_catamaran"] == "Sportif":
        cursor.execute(
            "SELECT * FROM catamaransportif WHERE id_catamaran = %s",
            (id_catamaran,)
        )
        sportif = cursor.fetchone()
        conn.close()

        return CatamaranSportif(
            cat["id_catamaran"],
            cat["nom"],
            cat["type_catamaran"],
            cat["longueur"],
            cat["largeur"],
            cat["hauteur"],
            cat["tirant_eau"],
            cat["vitesse_noeud"],
            cat["capacite"],
            cat["categorie_type_B"],
            sportif["foc"],
            sportif["derives_pivotantes"],
            sportif["grande_voile"]
        )

    conn.close()
    return None


def recuperer_evenements():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_evenement AS id,
            slug,
            nom,
            DATE_FORMAT(date_evenement, '%Y-%m-%d') AS date,
            lieu,
            image,
            statut,
            type_evenement,
            prix,
            places_prises,
            places_total,
            id_catamaran
        FROM evenements
        ORDER BY date_evenement ASC
    """)

    resultats = cursor.fetchall()
    conn.close()
    return resultats


def recuperer_evenement_par_slug(slug):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_evenement,
            slug,
            nom,
            DATE_FORMAT(date_evenement, '%Y-%m-%d') AS date,
            lieu,
            prix,
            places_prises,
            places_total,
            type_evenement,
            statut,
            image,
            id_catamaran
        FROM evenements
        WHERE slug = %s
    """, (slug,))

    evenement = cursor.fetchone()
    conn.close()

    if evenement:
        evenement["places_prises"] = calculer_places_prises_par_nom(evenement["nom"])

    return evenement


# ==============================
# PAGE ACCUEIL
# ==============================

@app.route("/")
def accueil():
    evenements = recuperer_evenements()
    evenements_a_venir = [e for e in evenements if e["statut"] == "avenir"][:3]

    resultats_data = recuperer_resultats()
    derniers_resultats = resultats_data[:3]

    return render_template(
        "accueil.html",
        evenements_a_venir=evenements_a_venir,
        derniers_resultats=derniers_resultats
    )


# ==============================
# PAGE ÉVÉNEMENTS
# ==============================

@app.route("/evenements")
def liste_evenements():
    lieu = request.args.get("lieu")
    tri = request.args.get("tri")

    resultats = recuperer_evenements()

    if lieu:
        resultats = [e for e in resultats if lieu.lower() in e["lieu"].lower()]

    if tri == "asc":
        resultats = sorted(resultats, key=lambda x: x["date"])
    elif tri == "desc":
        resultats = sorted(resultats, key=lambda x: x["date"], reverse=True)

    a_venir = [e for e in resultats if e["statut"] == "avenir"]
    passes = [e for e in resultats if e["statut"] == "passe"]

    return render_template(
        "evenements.html",
        a_venir=a_venir,
        passes=passes
    )


# ==============================
# PAGES DÉTAILLÉES DES ÉVÉNEMENTS
# ==============================

@app.route("/mediterranee", methods=["GET", "POST"])
def mediterranee():
    evenement = recuperer_evenement_par_slug("mediterranee")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    if request.method == "POST":
        if "user_id" not in session:
            flash("Vous devez être connecté pour réserver.", "error")
            return redirect(url_for("login"))

        user = recuperer_user(session["user_id"])
        places = int(request.form.get("places"))

        places_restantes = evenement["places_total"] - evenement["places_prises"]

        if places > places_restantes:
            flash(f"Il ne reste que {places_restantes} place(s).", "error")
            return redirect(url_for("mediterranee"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO inscriptions
                (user_id, prenom, nom, email, telephone, nombre_places, evenement, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user["id"],
                user["prenom"],
                user["nom"],
                user["email"],
                user["telephone"],
                places,
                evenement["nom"],
                "confirmee"
            ))

            conn.commit()
            mettre_a_jour_places_prises_par_nom(evenement["nom"])
            flash("Inscription confirmée !", "success")

        except Error:
            conn.rollback()
            flash("Erreur lors de l'inscription.", "error")

        conn.close()
        return redirect(url_for("mediterranee"))

    return render_template(
        "pages_detaillees/mediterranee.html",
        catamaran=catamaran,
        evenement=evenement
    )


@app.route("/atlantique", methods=["GET", "POST"])
def atlantique():
    evenement = recuperer_evenement_par_slug("atlantique")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    if request.method == "POST":
        if "user_id" not in session:
            flash("Vous devez être connecté pour réserver.", "error")
            return redirect(url_for("login"))

        user = recuperer_user(session["user_id"])
        places = int(request.form.get("places"))

        places_restantes = evenement["places_total"] - evenement["places_prises"]

        if places > places_restantes:
            flash(f"Il ne reste que {places_restantes} place(s).", "error")
            return redirect(url_for("atlantique"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                INSERT INTO inscriptions
                (user_id, prenom, nom, email, telephone, nombre_places, evenement, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user["id"],
                user["prenom"],
                user["nom"],
                user["email"],
                user["telephone"],
                places,
                evenement["nom"],
                "confirmee"
            ))

            if evenement["type_evenement"] == "Loisir":
                cursor.execute("""
                    SELECT id_passager
                    FROM passager
                    WHERE email = %s
                """, (user["email"],))
                passager = cursor.fetchone()

                if passager:
                    id_passager = passager["id_passager"]
                else:
                    cursor.execute("""
                        INSERT INTO passager (nom, prenom, telephone, email)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        user["nom"],
                        user["prenom"],
                        user["telephone"],
                        user["email"]
                    ))
                    id_passager = cursor.lastrowid

                cursor.execute("""
                    INSERT IGNORE INTO occuper (id_catamaran, id_passager)
                    VALUES (%s, %s)
                """, (
                    evenement["id_catamaran"],
                    id_passager
                ))

            conn.commit()
            mettre_a_jour_places_prises_par_nom(evenement["nom"])
            flash("Inscription confirmée !", "success")

        except Exception:
            conn.rollback()
            flash("Erreur lors de l'inscription.", "error")

        conn.close()
        return redirect(url_for("atlantique"))

    return render_template(
        "pages_detaillees/atlantique.html",
        catamaran=catamaran,
        evenement=evenement
    )


@app.route("/cotedazur", methods=["GET", "POST"])
def cotedazur():
    evenement = recuperer_evenement_par_slug("cotedazur")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    if request.method == "POST":
        if "user_id" not in session:
            flash("Vous devez être connecté pour réserver.", "error")
            return redirect(url_for("login"))

        user = recuperer_user(session["user_id"])
        places = int(request.form.get("places"))

        places_restantes = evenement["places_total"] - evenement["places_prises"]

        if places > places_restantes:
            flash(f"Il ne reste que {places_restantes} place(s).", "error")
            return redirect(url_for("cotedazur"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO inscriptions
                (user_id, prenom, nom, email, telephone, nombre_places, evenement, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user["id"],
                user["prenom"],
                user["nom"],
                user["email"],
                user["telephone"],
                places,
                evenement["nom"],
                "confirmee"
            ))

            conn.commit()
            mettre_a_jour_places_prises_par_nom(evenement["nom"])
            flash("Inscription confirmée !", "success")

        except Error:
            conn.rollback()
            flash("Erreur lors de l'inscription.", "error")

        conn.close()
        return redirect(url_for("cotedazur"))

    return render_template(
        "pages_detaillees/cotedazur.html",
        catamaran=catamaran,
        evenement=evenement
    )


@app.route("/calanque")
def calanque():
    evenement = recuperer_evenement_par_slug("calanque")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    return render_template(
        "pages_detaillees/calanque.html",
        catamaran=catamaran,
        evenement=evenement
    )


@app.route("/rochelle")
def rochelle():
    evenement = recuperer_evenement_par_slug("rochelle")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    return render_template(
        "pages_detaillees/rochelle.html",
        catamaran=catamaran,
        evenement=evenement
    )


@app.route("/golfe")
def golfe():
    evenement = recuperer_evenement_par_slug("golfe")
    catamaran = recuperer_catamaran(evenement["id_catamaran"])

    return render_template(
        "pages_detaillees/golfe.html",
        catamaran=catamaran,
        evenement=evenement
    )


# ==============================
# Page Résultats
# ==============================

def recuperer_resultats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            slug_evenement,
            nom_evenement,
            DATE_FORMAT(date_evenement, '%Y-%m-%d') AS date_evenement,
            type_evenement,
            rang,
            equipe,
            temps
        FROM resultats
        ORDER BY date_evenement DESC, rang ASC
    """)

    lignes = cursor.fetchall()
    conn.close()

    groupes = {}
    for ligne in lignes:
        slug = ligne["slug_evenement"]

        if slug not in groupes:
            groupes[slug] = {
                "slug_evenement": ligne["slug_evenement"],
                "nom_evenement": ligne["nom_evenement"],
                "date_evenement": ligne["date_evenement"],
                "type_evenement": ligne["type_evenement"],
                "classement": []
            }

        if ligne["rang"] != 0:
            groupes[slug]["classement"].append({
                "rang": ligne["rang"],
                "equipe": ligne["equipe"],
                "temps": ligne["temps"]
            })

    return list(groupes.values())


@app.route("/resultats")
def resultats():
    resultats_data = recuperer_resultats()
    return render_template("resultats.html", resultats=resultats_data)


# ==============================
# INFOS PRATIQUES
# ==============================

@app.route("/infos_pratiques")
def infos_pratiques():
    return render_template("infos_pratiques.html")


# ==============================
# PAGE CONTACT
# ==============================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom")
        email = request.form.get("email")
        sujet = request.form.get("sujet")
        message = request.form.get("message")
        captcha = request.form.get("captcha")

        if int(captcha) != session.get("captcha_result"):
            flash("La réponse au calcul est incorrecte. Veuillez réessayer.", "error")
            return redirect(url_for("contact"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO messages_contact
                (nom, email, sujet, message)
                VALUES (%s, %s, %s, %s)
            """, (nom, email, sujet, message))

            conn.commit()
            flash("Message envoyé ! Nous vous répondrons rapidement.", "success")

        except Error:
            flash("Erreur lors de l'envoi du message.", "error")

        conn.close()
        return redirect(url_for("contact"))

    a = random.randint(10, 50)
    b = random.randint(1, 10)
    session["captcha_result"] = a + b

    return render_template("contact.html", a=a, b=b)


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            flash("Connexion réussie", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("profil"))

        flash("Email ou mot de passe incorrect", "error")

    return render_template("login.html")


# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        prenom = request.form.get("prenom")
        nom = request.form.get("nom")
        telephone = request.form.get("telephone")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (prenom, nom, telephone, email, password, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (prenom, nom, telephone, email, password, "user"))

            conn.commit()
            flash("Compte créé avec succès !", "success")
            return redirect("/login")

        except Error:
            flash("Cet email possède déjà un compte.", "error")

        conn.close()

    return render_template("register.html")


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnexion réussie", "success")
    return redirect("/")


# ==============================
# PROFIL / RÉSERVATIONS
# ==============================

@app.route("/profil")
@login_required
def profil():
    if session.get("user_role") == "admin":
        return redirect(url_for("admin_dashboard"))

    user = recuperer_user(session["user_id"])
    reservations = recuperer_mes_reservations(session["user_id"])

    return render_template(
        "profil.html",
        user=user,
        reservations=reservations
    )


@app.route("/mes_reservations")
@login_required
def mes_reservations():
    if session.get("user_role") == "admin":
        return redirect(url_for("admin_dashboard"))

    reservations = recuperer_mes_reservations(session["user_id"])
    return render_template("mes_reservations.html", reservations=reservations)


@app.route("/mes_reservations/delete/<int:id_inscription>")
@login_required
def user_delete_reservation(id_inscription):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_inscription, evenement, user_id
        FROM inscriptions
        WHERE id_inscription = %s
    """, (id_inscription,))
    reservation = cursor.fetchone()

    if reservation and reservation["user_id"] == session["user_id"]:
        nom_evenement = reservation["evenement"]

        cursor.execute("""
            DELETE FROM inscriptions
            WHERE id_inscription = %s
        """, (id_inscription,))
        conn.commit()
        conn.close()

        mettre_a_jour_places_prises_par_nom(nom_evenement)
        flash("Réservation annulée.", "success")
        return redirect(url_for("mes_reservations"))

    conn.close()
    flash("Réservation introuvable.", "error")
    return redirect(url_for("mes_reservations"))


# ==============================
# ADMIN
# ==============================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    total_users = compter_utilisateurs()
    total_reservations = compter_reservations()
    reservations = recuperer_toutes_reservations()

    user = recuperer_user(session["user_id"])

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_reservations=total_reservations,
        reservations=reservations,
        user=user
    )


@app.route("/admin/reservations")
@admin_required
def admin_reservations():
    reservations = recuperer_toutes_reservations()
    return render_template("admin_reservations.html", reservations=reservations)


@app.route("/admin/reservations/delete/<int:id_inscription>")
@admin_required
def admin_delete_reservation(id_inscription):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_inscription, evenement
        FROM inscriptions
        WHERE id_inscription = %s
    """, (id_inscription,))
    reservation = cursor.fetchone()

    if reservation:
        nom_evenement = reservation["evenement"]

        cursor.execute("""
            DELETE FROM inscriptions
            WHERE id_inscription = %s
        """, (id_inscription,))
        conn.commit()
        conn.close()

        mettre_a_jour_places_prises_par_nom(nom_evenement)
        flash("Réservation supprimée.", "success")
        return redirect(url_for("admin_reservations"))

    conn.close()
    flash("Réservation introuvable.", "error")
    return redirect(url_for("admin_reservations"))


# ==============================
# NEWSLETTER
# ==============================

@app.route("/newsletter", methods=["POST"])
def newsletter():
    email = request.form.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO newsletter (email) VALUES (%s)",
            (email,)
        )
        conn.commit()
        flash("Merci pour votre inscription à la newsletter", "success")

    except Error:
        flash("Cet email est déjà inscrit à la newsletter", "error")

    conn.close()
    return redirect(request.referrer)


# ==============================
# LANCEMENT
# ==============================

if __name__ == "__main__":
    app.run(debug=True)















