from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.exc import IntegrityError


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "change-me-very-secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@127.0.0.1:3306/evidencija?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

# ---------- MODELI ----------
class Korisnik(db.Model):
    __tablename__ = "korisnici"

    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(100), nullable=False)
    prezime = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # hash
    tip_korisnika = db.Column(db.Enum("korisnik", "admin"), nullable=False, default="korisnik")
    datum_kreiranja = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    rezervacije = db.relationship("Rezervacija", backref="korisnik", lazy=True)

class Termin(db.Model):
    __tablename__ = "termini"

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.Text, nullable=True)
    datum = db.Column(db.Date, nullable=False)
    vreme = db.Column(db.Time, nullable=False)
    trajanje = db.Column(db.Integer, nullable=False, default=60)  
    max_korisnika = db.Column(db.Integer, nullable=False, default=1)
    kreirao_id = db.Column(db.Integer, db.ForeignKey("korisnici.id"), nullable=False)

    
    status = db.Column(db.Enum("dostupan", "zauzet", "otkazan"), nullable=False, default="dostupan")

    datum_kreiranja = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    rezervacije = db.relationship("Rezervacija", backref="termin", lazy=True)

class Rezervacija(db.Model):
    __tablename__ = "rezervacije"
    id = db.Column(db.Integer, primary_key=True)
    korisnik_id = db.Column(db.Integer, db.ForeignKey("korisnici.id"), nullable=False)
    termin_id = db.Column(db.Integer, db.ForeignKey("termini.id"), nullable=False)
    datum_rezervacije = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
    status = db.Column(db.Enum("aktivna", "otkazana", "zavrsena"), nullable=False, default="aktivna")

    napomena = db.Column(db.Text, nullable=True)
    __table_args__ = (db.UniqueConstraint("korisnik_id", "termin_id", name="uq_korisnik_termin"),)


# ---------- HELPERI ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if session.get("tip_korisnika") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

def izracunaj_popunjenost(termin_id: int) -> int:

    return Rezervacija.query.filter_by(termin_id=termin_id, status="aktivna").count()

def osvezi_status_termina(termin: Termin) -> None:
    if termin.status == "otkazan":
        return
    popunjeno = izracunaj_popunjenost(termin.id)
    if popunjeno >= termin.max_korisnika:
        termin.status = "zauzet"
    else:
        termin.status = "dostupan"
    db.session.commit()

def current_user():
    if "user_id" in session:
        return Korisnik.query.get(session["user_id"])
    return None

def izracunaj_popunjenost(termin_id: int) -> int:
    return Rezervacija.query.filter_by(termin_id=termin_id, status="potvrdjeno").count()

def osvezi_status_termina(termin: Termin) -> None:
    """Automatski setuje status na 'zauzet' kad je pun, 'dostupan' kad ima mesta.
       Ako je 'otkazan', ne diramo ga automatski."""
    if termin.status == "otkazan":
        return
    popunjeno = izracunaj_popunjenost(termin.id)
    if popunjeno >= termin.max_korisnika:
        termin.status = "zauzet"
    else:
        termin.status = "dostupan"
    db.session.commit()

# ---------- AUTH ----------
@app.route("/", methods=["GET"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("tip_korisnika") == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("korisnik_dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = Korisnik.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["tip_korisnika"] = user.tip_korisnika
            flash("Uspešno ste se prijavili.", "success")
            return redirect(url_for("home"))
        flash("Pogrešan email ili lozinka.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ime = request.form.get("ime", "").strip()
        prezime = request.form.get("prezime", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not all([ime, prezime, email, password, password2]):
            flash("Sva polja su obavezna.", "warning")
            return render_template("register.html")

        if password != password2:
            flash("Lozinke se ne poklapaju.", "warning")
            return render_template("register.html")

        if Korisnik.query.filter_by(email=email).first():
            flash("Nalog sa tim email-om već postoji.", "warning")
            return render_template("register.html")

        user = Korisnik(
            ime=ime,
            prezime=prezime,
            email=email,
            password=generate_password_hash(password),
            tip_korisnika="korisnik",
        )
        db.session.add(user)
        db.session.commit()
        flash("Registracija uspešna. Možete se prijaviti.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Odjavljeni ste.", "info")
    return redirect(url_for("login"))

# ---------- KORISNIK ----------
@app.route("/korisnik")
@login_required
@role_required("korisnik", "admin")
def korisnik_dashboard():
    user = current_user()

    subq = db.session.query(
        Rezervacija.termin_id,
        func.count(Rezervacija.id).label("rezv")
    ).filter(Rezervacija.status == "aktivna") \
     .group_by(Rezervacija.termin_id).subquery()

    dostupni_broj = db.session.query(Termin.id) \
        .outerjoin(subq, Termin.id == subq.c.termin_id) \
        .filter(
            Termin.status != "otkazan",
            func.date(Termin.datum) >= datetime.utcnow().date(),
            func.coalesce(subq.c.rezv, 0) < Termin.max_korisnika
        ).count()

    moje_broj = Rezervacija.query.filter_by(
        korisnik_id=user.id, status="aktivna"
    ).count()

    return render_template("index.html",
                           user=user,
                           dostupni_broj=dostupni_broj,
                           moje_broj=moje_broj)

@app.route("/termini")
@login_required
def lista_termina():
    subq = db.session.query(
        Rezervacija.termin_id,
        func.count(Rezervacija.id).label("rezv")
    ).filter(Rezervacija.status == "aktivna") \
     .group_by(Rezervacija.termin_id).subquery()

    # vraćamo SAMO termine koji:
    # - nisu otkazani
    # - su u budućnosti
    # - NISU puni (rezv < max_korisnika)
    termini = db.session.query(
        Termin,
        func.coalesce(subq.c.rezv, 0).label("popunjeno")
    ).outerjoin(subq, Termin.id == subq.c.termin_id).filter(
        Termin.status != "otkazan",
        func.date(Termin.datum) >= datetime.utcnow().date(),
        func.coalesce(subq.c.rezv, 0) < Termin.max_korisnika
    ).order_by(Termin.datum.asc(), Termin.vreme.asc()).all()

    return render_template("lista_termina.html", termini=termini)


@app.route("/rezervisi/<int:termin_id>", methods=["POST"])
@login_required
def rezervisi(termin_id):
    user = current_user()
    termin = Termin.query.get_or_404(termin_id)

    # ne dozvoli za otkazan termin
    if termin.status == "otkazan":
        flash("Termin je otkazan.", "warning")
        return redirect(url_for("lista_termina"))

    # pun?
    zauzeto = izracunaj_popunjenost(termin.id)   # broji samo status='aktivna'
    if zauzeto >= termin.max_korisnika:
        termin.status = "zauzet"
        db.session.commit()
        flash("Termin je pun (zauzet).", "warning")
        return redirect(url_for("lista_termina"))

    # 1) već AKTIVAN za isti termin?
    aktivna = Rezervacija.query.filter_by(
        korisnik_id=user.id, termin_id=termin.id, status="aktivna"
    ).first()
    if aktivna:
        flash("Već imate rezervaciju za ovaj termin.", "info")
        return redirect(url_for("moji_termini"))

    # 2) konflikt (isti datum i vreme već rezervisani za neki drugi termin)
    konflikt = (db.session.query(Rezervacija.id)
        .join(Termin, Termin.id == Rezervacija.termin_id)
        .filter(
            Rezervacija.korisnik_id == user.id,
            Rezervacija.status == "aktivna",
            Termin.datum == termin.datum,
            Termin.vreme == termin.vreme,
            Rezervacija.termin_id != termin.id  # nije isti termin (to je već pokriveno gore)
        )
        .first())
    if konflikt:
        flash("Već ste zakazali uslugu u ovom terminu.", "warning")
        return redirect(url_for("lista_termina"))

    # 3) postoji ranije OTKAZAN za isti termin? -> reaktiviraj
    otkazana = Rezervacija.query.filter(
        Rezervacija.korisnik_id == user.id,
        Rezervacija.termin_id == termin.id,
        Rezervacija.status.in_(["otkazana", "otkazano"])
    ).first()
    if otkazana:
        otkazana.status = "aktivna"
        otkazana.datum_rezervacije = datetime.utcnow()
        db.session.commit()
        osvezi_status_termina(termin)
        flash("Rezervacija je ponovo aktivirana.", "success")
        return redirect(url_for("moji_termini"))

    # 4) nema ništa -> napravi novu
    r = Rezervacija(korisnik_id=user.id, termin_id=termin.id, status="aktivna")
    db.session.add(r)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Već imate rezervaciju za ovaj termin.", "info")
        return redirect(url_for("moji_termini"))

    osvezi_status_termina(termin)
    flash("Termin rezervisan.", "success")
    return redirect(url_for("moji_termini"))


@app.route("/moji-termini")
@login_required
def moji_termini():
    user = current_user()
    moje = Rezervacija.query.join(Termin, Rezervacija.termin_id == Termin.id)\
        .filter(Rezervacija.korisnik_id == user.id)\
        .order_by(Termin.datum.desc(), Termin.vreme.desc())\
        .all()
    return render_template("moji_termini.html", rezervacije=moje, now=datetime.utcnow())

@app.route("/otkazi/<int:rez_id>", methods=["POST"])
@login_required
def otkazi_rez(rez_id):
    r = Rezervacija.query.get_or_404(rez_id)
    if session.get("tip_korisnika") != "admin" and r.korisnik_id != session.get("user_id"):
        abort(403)
    r.status = "otkazana"
    db.session.commit()

    # ako je termin bio pun, možda sada više nije → vrati u 'dostupan'
    termin = Termin.query.get(r.termin_id)
    osvezi_status_termina(termin)

    flash("Rezervacija otkazana.", "info")
    return redirect(request.referrer or url_for("moji_termini"))

# ---------- ADMIN ----------
@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    ukupno_korisnika = Korisnik.query.count()
    ukupno_termina = Termin.query.count()
    ukupno_rez = Rezervacija.query.count()
    return render_template("admin/index.html",
                           ukupno_korisnika=ukupno_korisnika,
                           ukupno_termina=ukupno_termina,
                           ukupno_rez=ukupno_rez)

@app.route("/admin/termini")
@role_required("admin")
def admin_termini():
    subq = db.session.query(
        Rezervacija.termin_id,
        func.count(Rezervacija.id).label("rezv")
    ).filter(Rezervacija.status == "aktivna") \
     .group_by(Rezervacija.termin_id).subquery()

    termini = db.session.query(
        Termin,
        func.coalesce(subq.c.rezv, 0).label("popunjeno")
    ).outerjoin(subq, Termin.id == subq.c.termin_id) \
     .order_by(Termin.datum.desc(), Termin.vreme.desc()).all()

    return render_template("admin/termini.html", termini=termini)

@app.route("/admin/termini/novi", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_termin_novi():
    if request.method == "POST":
        naziv = request.form.get("naziv", "").strip()
        opis = request.form.get("opis", "").strip()
        datum = request.form.get("datum")
        vreme = request.form.get("vreme")
        trajanje = int(request.form.get("trajanje", 60) or 60)
        max_korisnika = int(request.form.get("max_korisnika", 1) or 1)
        status = request.form.get("status", "dostupan")  # default novi

        if not all([naziv, datum, vreme]):
            flash("Naziv, datum i vreme su obavezni.", "warning")
            return render_template("admin/novi_termini.html")

        t = Termin(
            naziv=naziv,
            opis=opis or None,
            datum=datetime.strptime(datum, "%Y-%m-%d").date(),
            vreme=datetime.strptime(vreme, "%H:%M").time(),
            trajanje=trajanje,
            max_korisnika=max_korisnika,
            kreirao_id=session["user_id"],
            status=status
        )
        db.session.add(t)
        db.session.commit()

        # Ako novi termin nije otkazan, izračunaj realan status po popunjenosti
        osvezi_status_termina(t)
        flash("Termin dodat.", "success")
        return redirect(url_for("admin_termini"))
    return render_template("admin/novi_termini.html")

@app.route("/admin/termini/<int:tid>/uredi", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_termin_uredi(tid):
    t = Termin.query.get_or_404(tid)
    if request.method == "POST":
        t.naziv = request.form.get("naziv", t.naziv)
        t.opis = request.form.get("opis", t.opis)
        t.datum = datetime.strptime(request.form.get("datum"), "%Y-%m-%d").date()
        t.vreme = datetime.strptime(request.form.get("vreme"), "%H:%M").time()
        t.trajanje = int(request.form.get("trajanje", t.trajanje))
        t.max_korisnika = int(request.form.get("max_korisnika", t.max_korisnika))
        t.status = request.form.get("status", t.status)  # može ručno da proglasi 'otkazan'
        db.session.commit()

        # ako nije otkazan, osveži po popunjenosti
        osvezi_status_termina(t)
        flash("Termin ažuriran.", "success")
        return redirect(url_for("admin_termini"))
    return render_template("admin/uredi_termin.html", t=t)

@app.route("/admin/termini/<int:tid>/obrisi", methods=["POST"])
@login_required
@role_required("admin")
def admin_termin_obrisi(tid):
    t = Termin.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    flash("Termin obrisan.", "info")
    return redirect(url_for("admin_termini"))

@app.route("/admin/korisnici")
@login_required
@role_required("admin")
def admin_korisnici():
    korisnici = Korisnik.query.order_by(Korisnik.datum_kreiranja.desc()).all()
    return render_template("admin/korisnici.html", korisnici=korisnici)

@app.route("/admin/korisnici/<int:uid>/uredi", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_korisnik_uredi(uid):
    k = Korisnik.query.get_or_404(uid)
    if request.method == "POST":
        k.ime = request.form.get("ime", k.ime)
        k.prezime = request.form.get("prezime", k.prezime)
        k.email = request.form.get("email", k.email).lower()
        k.tip_korisnika = request.form.get("tip_korisnika", k.tip_korisnika)
        nova_lozinka = request.form.get("password", "")
        if nova_lozinka:
            k.password = generate_password_hash(nova_lozinka)
        db.session.commit()
        flash("Korisnik ažuriran.", "success")
        return redirect(url_for("admin_korisnici"))
    return render_template("admin/uredi_korisnika.html", k=k)

@app.route("/admin/rezervacije")
@login_required
@role_required("admin")
def admin_rezervacije():
    rez = Rezervacija.query.order_by(Rezervacija.datum_rezervacije.desc()).all()
    return render_template("admin/rezervacije.html", rezervacije=rez)

# ---------- ERROR HANDLERS ----------
@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def notfound(e):
    return render_template("errors/404.html"), 404

# ---------- MAIN ----------
if __name__ == "__main__":
    from sqlalchemy import text as _text
    with app.app_context():
        try:
            db.session.execute(_text("SELECT 1"))
            print("DB konekcija OK ✔")
        except Exception as e:
            print("DB konekcija NE RADI ✖", e)
    app.run(debug=True)
