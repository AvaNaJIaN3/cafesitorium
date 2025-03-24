from flask import Flask, redirect, render_template, url_for, flash
from sqlalchemy import Integer, String, Boolean
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, BooleanField
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"

class Base(DeclarativeBase):
    pass

# Creating DB fundamentals
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    __tablename__ = 'cafe'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    map_url:Mapped[str] = mapped_column(String, nullable=False)
    img_url:Mapped[str] = mapped_column(String, nullable=False)
    location:Mapped[str] = mapped_column(String, nullable=False)
    has_sockets:Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet : Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi : Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls : Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats : Mapped[str] = mapped_column(String, nullable=False)
    coffee_price : Mapped[str] = mapped_column(String, nullable=False)

with app.app_context():
    db.create_all()

class AddCafe(FlaskForm):
    name = StringField("The name of your cafe", validators=[DataRequired()])
    map_url = StringField("Location url", validators=[DataRequired()])
    img_url = StringField("Image url", validators=[DataRequired()])
    location = StringField('Location name', validators=[DataRequired()])
    has_sockets = BooleanField("Has sockets?")
    has_toilet = BooleanField('Has toilet?')
    has_wifi = BooleanField('Has Wi-Fi?')
    can_take_calls = BooleanField('Can take calls?')
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee price', validators=[DataRequired()])


@app.route('/')
def home():
    return render_template("home_page.html")

@app.route('/all_cafes')
def all_cafes():
    results = db.session.execute(db.Select(Cafe))
    cafes = results.scalars().all()
    return render_template('cafes.html', cafes=cafes)

@app.route('/cafe/<int:id>')
def cafe(id):
    cafe = Cafe.query.filter_by(id=id).first()
    if cafe is not None:
        return render_template('cafe.html', cafe=cafe)
    else:
        return redirect(url_for('home'))

@app.route('/add_cafe', methods=['GET', 'POST'])
def add_cafe():
    form = AddCafe()
    if form.validate_on_submit():
        check_cafe = Cafe.query.filter_by(name=form.name.data).first()
        if check_cafe is None:
            new_cafe = Cafe(name=form.name.data, map_url=form.map_url.data, img_url=form.img_url.data, location=form.location.data,
                            has_sockets=form.has_sockets.data, has_toilet = form.has_toilet.data, has_wifi = form.has_wifi.data,
                            can_take_calls = form.can_take_calls.data, seats = form.seats.data, coffee_price = form.coffee_price.data)
            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for('cafe', id=new_cafe.id))
        else:
            print("This cafe is already exists")
    return render_template('add_cafe.html', form=form)


from flask import flash


@app.route('/edit_cafe/<int:id>', methods=['GET', 'POST'])
def edit_cafe(id):
    cafe = Cafe.query.get(id)
    if cafe is None:
        return redirect(url_for('home'))

    edit_form = AddCafe(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        has_sockets=cafe.has_sockets,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        can_take_calls=cafe.can_take_calls,
        seats=cafe.seats,
        coffee_price=cafe.coffee_price
    )

    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.has_sockets = edit_form.has_sockets.data
        cafe.has_toilet = edit_form.has_toilet.data
        cafe.has_wifi = edit_form.has_wifi.data
        cafe.can_take_calls = edit_form.can_take_calls.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data
        db.session.commit()
        return redirect(url_for('cafe', id=cafe.id))

    return render_template('edit_cafe.html', form=edit_form, cafe=cafe)

@app.route('/delete_cafe/<int:id>')
def delete_cafe(id):
    cafe = Cafe.query.get(id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)