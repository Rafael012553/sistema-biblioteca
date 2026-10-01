from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def conectar_banco():
    banco = sqlite3.connect("biblioteca.db")
    banco.row_factory = sqlite3.Row
    return banco


def criar_tabelas():
    banco = conectar_banco()

    banco.execute("""
        CREATE TABLE IF NOT EXISTS autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    banco.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    banco.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id_livro INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            ano INTEGER,
            id_autor INTEGER NOT NULL,
            id_categoria INTEGER NOT NULL,
            FOREIGN KEY (id_autor) REFERENCES autores(id_autor),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    """)

    banco.commit()
    banco.close()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    banco = conectar_banco()

    if request.method == "POST":
        titulo = request.form["titulo"]
        ano = request.form["ano"]
        autor = request.form["autor"]
        categoria = request.form["categoria"]

        banco.execute(
            "INSERT INTO autores (nome) VALUES (?)",
            (autor,)
        )

        id_autor = banco.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        banco.execute(
            "INSERT INTO categorias (nome) VALUES (?)",
            (categoria,)
        )

        id_categoria = banco.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        banco.execute("""
            INSERT INTO livros
            (titulo, ano, id_autor, id_categoria)
            VALUES (?, ?, ?, ?)
        """, (titulo, ano, id_autor, id_categoria))

        banco.commit()
        banco.close()

        return redirect("/livros")

    banco.close()
    return render_template("cadastro.html")


@app.route("/livros")
def livros():
    banco = conectar_banco()

    livros = banco.execute("""
        SELECT
            livros.id_livro,
            livros.titulo,
            livros.ano,
            autores.nome AS autor,
            categorias.nome AS categoria
        FROM livros
        INNER JOIN autores
            ON livros.id_autor = autores.id_autor
        INNER JOIN categorias
            ON livros.id_categoria = categorias.id_categoria
    """).fetchall()

    banco.close()

    return render_template("livros.html", livros=livros)


@app.route("/excluir/<int:id>")
def excluir(id):
    banco = conectar_banco()

    livro = banco.execute(
        "SELECT id_autor, id_categoria FROM livros WHERE id_livro = ?",
        (id,)
    ).fetchone()

    if livro:
        banco.execute(
            "DELETE FROM livros WHERE id_livro = ?",
            (id,)
        )

        banco.execute(
            "DELETE FROM autores WHERE id_autor = ?",
            (livro["id_autor"],)
        )

        banco.execute(
            "DELETE FROM categorias WHERE id_categoria = ?",
            (livro["id_categoria"],)
        )

    banco.commit()
    banco.close()

    return redirect("/livros")


if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)