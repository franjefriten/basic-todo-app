from flask import app, render_template, redirect, Response, jsonify, Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app=app, model_class=Base)

class TodoList(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    todo: Mapped[str] = mapped_column(db.String, nullable=False)

    def __str__(self):
        return f"{self.id}: {self.todo}"

with app.app_context():
    db.drop_all()
    db.create_all()

    db.session.add(TodoList(todo="Limpiar"))
    db.session.add(TodoList(todo="Sexo"))
    db.session.add(TodoList(todo="Lanzarse por un precipicio"))

    db.session.commit()


def todo_serializer(todo):
    return {"id": todo.id, "todo": todo.todo}

@app.route("/", methods=["GET"])
def home():
    return jsonify([*map(todo_serializer, TodoList.query.all())])

@app.route("/todo-create", methods=["POST"])
def todo_create():
    request_data = json.loads(request.data)
    todo = TodoList(todo=request_data['todo'])

    with app.app_context():
        db.session.add(todo)
        db.session.commit()
    
    return jsonify({"201": "todo succesfully created"})

@app.route("/update/<int:id>", methods=["PUT"])
def update_todo(id):
    # edit todo item based on ID
    item = db.session.get(TodoList, id)
    data = request.get_json(force=True)
    todo = data["todo"]
    item.todo = todo
    db.session.commit()

    return jsonify({"200": "Updated successfully"})

@app.route("/<int:id>", methods=["POST"])
def delete_todo(id):
    # delete todo item from todo list
    db.session.delete(id=id)
    with app.app_context():
        db.session.commit()

    return jsonify({"204": "Delete successfully"})

if __name__ == "__main__":
    app.run(debug=True)