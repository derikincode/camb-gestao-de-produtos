from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import uuid
from PIL import Image
import io
from flask_wtf.csrf import CSRFProtect
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB por imagem
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa CSRF
csrf = CSRFProtect(app)

# Inicializa o banco de dados
def init_db():
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    codigo TEXT NOT NULL,
                    descricao TEXT,
                    altura REAL,
                    largura REAL,
                    comprimento REAL,
                    peso REAL,
                    marca TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    caminho TEXT NOT NULL,
                    descricao TEXT,  -- Nova coluna para descrição da imagem
                    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE
                )
            ''')
            # Adiciona colunas se necessário
            cursor.execute("PRAGMA table_info(produtos)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'peso' not in columns:
                cursor.execute('ALTER TABLE produtos ADD COLUMN peso REAL')
            if 'marca' not in columns:
                cursor.execute('ALTER TABLE produtos ADD COLUMN marca TEXT')
            # Adiciona coluna descricao na tabela imagens se não existir
            cursor.execute("PRAGMA table_info(imagens)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'descricao' not in columns:
                cursor.execute('ALTER TABLE imagens ADD COLUMN descricao TEXT')
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        raise

# Verifica extensões permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Valida dimensões da imagem
def validate_image_dimensions(file):
    try:
        img = Image.open(file)
        max_width, max_height = 2000, 2000
        if img.width > max_width or img.height > max_height:
            return False
        file.seek(0)
        return True
    except Exception as e:
        logger.error(f"Erro ao validar dimensões da imagem: {e}")
        return False

# Comprime imagem
def compress_image(file):
    try:
        img = Image.open(file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=75)
        output.seek(0)
        return output
    except Exception as e:
        logger.error(f"Erro ao comprimir imagem: {e}")
        return None

# Inicialização
try:
    init_db()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
except Exception as e:
    logger.error(f"Erro durante inicialização: {e}")
    raise

@app.route('/')
def index():
    search = request.args.get('search', '').strip()
    try:
        with sqlite3.connect('database.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.nome, p.codigo, p.descricao, p.altura, p.largura, p.comprimento, p.peso, p.marca,
                       GROUP_CONCAT(i.id) as imagem_ids, 
                       GROUP_CONCAT(i.caminho) as imagem_caminhos,
                       GROUP_CONCAT(i.descricao) as imagem_descricoes
                FROM produtos p
                LEFT JOIN imagens i ON p.id = i.produto_id
                %s
                GROUP BY p.id
            """
            params = []
            if search:
                query = query % "WHERE p.nome LIKE ? OR p.codigo LIKE ?"
                params = [f'%{search}%', f'%{search}%']
            else:
                query = query % ""
            cursor.execute(query, params)
            produtos = cursor.fetchall()

            produtos_com_imagens = []
            for p in produtos:
                imagens = []
                if p['imagem_ids'] and p['imagem_caminhos']:
                    ids = p['imagem_ids'].split(',')
                    caminhos = p['imagem_caminhos'].split(',')
                    descricoes = p['imagem_descricoes'].split(',') if p['imagem_descricoes'] else [''] * len(ids)
                    if len(ids) == len(caminhos) == len(descricoes):
                        imagens = list(zip(ids, caminhos, descricoes))
                    else:
                        logger.warning(f"Número de IDs, caminhos ou descrições não coincidem para o produto {p['id']}")
                produtos_com_imagens.append((p, imagens))

        return render_template('index.html', produtos=produtos_com_imagens, search=search)
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        flash("Erro ao carregar produtos.", "danger")
        return render_template('index.html', produtos=[], search=search)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        codigo = request.form['codigo'].strip()
        descricao = request.form['descricao'].strip()
        altura = request.form['altura'].strip()
        largura = request.form['largura'].strip()
        comprimento = request.form['comprimento'].strip()
        peso = request.form['peso'].strip()
        marca = request.form['marca'].strip()
        fotos = request.files.getlist('fotos[]')
        fotos_desc = request.form.getlist('fotos_desc[]')

        # Validações
        if not nome or len(nome) > 100:
            flash("Nome inválido ou muito longo.", "danger")
            return redirect(url_for('cadastrar'))
        if not codigo or len(codigo) > 50:
            flash("Código inválido ou muito longo.", "danger")
            return redirect(url_for('cadastrar'))
        if len(fotos) > 10:
            flash("Limite de até 10 imagens por produto.", "danger")
            return redirect(url_for('cadastrar'))
        if marca not in ['B. Braun', 'Cremer', 'Mucambo', 'Nipro', 'Bio Higienic']:
            flash("Marca inválida. Escolha entre B. Braun, Cremer, Mucambo, Nipro ou Bio Higienic.", "danger")
            return redirect(url_for('cadastrar'))
        if len(descricao) > 300:
            flash("Descrição excede o limite de 300 caracteres.", "danger")
            return redirect(url_for('cadastrar'))
        if len(fotos) != len(fotos_desc):
            flash("Número de descrições não corresponde ao número de imagens.", "danger")
            return redirect(url_for('cadastrar'))
        for desc in fotos_desc:
            if desc and len(desc) > 300:
                flash("Descrição da imagem excede o limite de 300 caracteres.", "danger")
                return redirect(url_for('cadastrar'))
        try:
            altura = float(altura) if altura else None
            largura = float(largura) if largura else None
            comprimento = float(comprimento) if comprimento else None
            peso = float(peso) if peso else None
            if any(x is not None and x <= 0 for x in [altura, largura, comprimento, peso]):
                flash("Dimensões ou peso não podem ser negativos ou zero.", "danger")
                return redirect(url_for('cadastrar'))
        except ValueError:
            flash("Dimensões ou peso devem ser números válidos.", "danger")
            return redirect(url_for('cadastrar'))

        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM produtos WHERE codigo=?", (codigo,))
                if cursor.fetchone():
                    flash("Código já existe.", "danger")
                    return redirect(url_for('cadastrar'))

                cursor.execute('''
                    INSERT INTO produtos (nome, codigo, descricao, altura, largura, comprimento, peso, marca)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nome, codigo, descricao, altura, largura, comprimento, peso, marca))
                produto_id = cursor.lastrowid

                for foto, foto_desc in zip(fotos, fotos_desc):
                    if foto and allowed_file(foto.filename):
                        if not validate_image_dimensions(foto):
                            flash("Imagem excede dimensões máximas (2000x2000px).", "danger")
                            continue
                        compressed_image = compress_image(foto)
                        if compressed_image is None:
                            flash("Erro ao comprimir imagem.", "danger")
                            continue
                        filename = f"{uuid.uuid4().hex}.jpg"
                        caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        try:
                            with open(caminho, 'wb') as f:
                                f.write(compressed_image.read())
                            cursor.execute('''
                                INSERT INTO imagens (produto_id, caminho, descricao) VALUES (?, ?, ?)
                            ''', (produto_id, filename, foto_desc.strip() if foto_desc else None))
                        except Exception as e:
                            logger.error(f"Erro ao salvar imagem: {e}")
                            flash("Erro ao salvar imagem.", "danger")

                conn.commit()
            flash("Produto cadastrado com sucesso!", "success")
            return redirect(url_for('index'))
        except sqlite3.Error as e:
            logger.error(f"Erro ao cadastrar produto: {e}")
            flash("Erro ao cadastrar produto.", "danger")
            return redirect(url_for('cadastrar'))

    return render_template('form.html', produto=None, imagens=[])

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    try:
        with sqlite3.connect('database.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if request.method == 'POST':
                nome = request.form['nome'].strip()
                codigo = request.form['codigo'].strip()
                descricao = request.form['descricao'].strip()
                altura = request.form['altura'].strip()
                largura = request.form['largura'].strip()
                comprimento = request.form['comprimento'].strip()
                peso = request.form['peso'].strip()
                marca = request.form['marca'].strip()
                novas_fotos = request.files.getlist('fotos[]')
                novas_fotos_desc = request.form.getlist('fotos_desc[]')
                existing_images_desc = request.form.to_dict(flat=False).get('existing_images_desc', {})

                if not nome or len(nome) > 100:
                    flash("Nome inválido ou muito longo.", "danger")
                    return redirect(url_for('editar', id=id))
                if not codigo or len(codigo) > 50:
                    flash("Código inválido ou muito longo.", "danger")
                    return redirect(url_for('editar', id=id))
                if marca not in ['B. Braun', 'Cremer', 'Mucambo', 'Nipro', 'Bio Higienic']:
                    flash("Marca inválida. Escolha entre B. Braun, Cremer, Mucambo, Nipro ou Bio Higienic.", "danger")
                    return redirect(url_for('editar', id=id))
                if len(descricao) > 300:
                    flash("Descrição excede o limite de 300 caracteres.", "danger")
                    return redirect(url_for('editar', id=id))
                if len(novas_fotos) != len(novas_fotos_desc):
                    flash("Número de descrições não corresponde ao número de novas imagens.", "danger")
                    return redirect(url_for('editar', id=id))
                for desc in novas_fotos_desc:
                    if desc and len(desc) > 300:
                        flash("Descrição da nova imagem excede o limite de 300 caracteres.", "danger")
                        return redirect(url_for('editar', id=id))
                for desc in existing_images_desc.values():
                    if desc and len(desc[0]) > 300:
                        flash("Descrição da imagem existente excede o limite de 300 caracteres.", "danger")
                        return redirect(url_for('editar', id=id))
                try:
                    altura = float(altura) if altura else None
                    largura = float(largura) if largura else None
                    comprimento = float(comprimento) if comprimento else None
                    peso = float(peso) if peso else None
                    if any(x is not None and x <= 0 for x in [altura, largura, comprimento, peso]):
                        flash("Dimensões ou peso não podem ser negativos ou zero.", "danger")
                        return redirect(url_for('editar', id=id))
                except ValueError:
                    flash("Dimensões ou peso devem ser números válidos.", "danger")
                    return redirect(url_for('editar', id=id))

                cursor.execute("SELECT id FROM produtos WHERE codigo=? AND id!=?", (codigo, id))
                if cursor.fetchone():
                    flash("Código já existe.", "danger")
                    return redirect(url_for('editar', id=id))

                cursor.execute('''
                    UPDATE produtos SET nome=?, codigo=?, descricao=?, altura=?, largura=?, comprimento=?, peso=?, marca=? WHERE id=?
                ''', (nome, codigo, descricao, altura, largura, comprimento, peso, marca, id))

                # Atualiza descrições das imagens existentes
                for img_id, desc in existing_images_desc.items():
                    desc = desc[0].strip() if desc and desc[0] else None
                    cursor.execute('''
                        UPDATE imagens SET descricao=? WHERE id=?
                    ''', (desc, img_id))

                # Adiciona novas imagens
                for foto, foto_desc in zip(novas_fotos, novas_fotos_desc):
                    if foto and allowed_file(foto.filename):
                        if not validate_image_dimensions(foto):
                            flash("Imagem excede dimensões máximas (2000x2000px).", "danger")
                            continue
                        compressed_image = compress_image(foto)
                        if compressed_image is None:
                            flash("Erro ao comprimir imagem.", "danger")
                            continue
                        filename = f"{uuid.uuid4().hex}.jpg"
                        caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        try:
                            with open(caminho, 'wb') as f:
                                f.write(compressed_image.read())
                            cursor.execute('''
                                INSERT INTO imagens (produto_id, caminho, descricao) VALUES (?, ?, ?)
                            ''', (id, filename, foto_desc.strip() if foto_desc else None))
                        except Exception as e:
                            logger.error(f"Erro ao salvar imagem: {e}")
                            flash("Erro ao salvar imagem.", "danger")

                conn.commit()
                flash("Produto atualizado com sucesso!", "success")
                return redirect(url_for('index'))

            cursor.execute("SELECT * FROM produtos WHERE id=?", (id,))
            produto = cursor.fetchone()
            if not produto:
                flash("Produto não encontrado.", "danger")
                return redirect(url_for('index'))

            cursor.execute("SELECT id, caminho, descricao FROM imagens WHERE produto_id=?", (id,))
            imagens = cursor.fetchall()

            logger.info(f"Produto encontrado: {dict(produto)}")
            logger.info(f"Imagens encontradas: {imagens}")

        return render_template('form.html', produto=dict(produto), imagens=imagens)
    except sqlite3.Error as e:
        logger.error(f"Erro ao editar produto: {e}")
        flash("Erro ao carregar produto.", "danger")
        return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho FROM imagens WHERE produto_id=?", (id,))
            imagens = cursor.fetchall()
            for img in imagens:
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], img[0])
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")

            cursor.execute("DELETE FROM imagens WHERE produto_id=?", (id,))
            cursor.execute("DELETE FROM produtos WHERE id=?", (id,))
            conn.commit()

        flash("Produto excluído com sucesso!", "success")
        return redirect(url_for('index'))
    except sqlite3.Error as e:
        logger.error(f"Erro ao deletar produto: {e}")
        flash("Erro ao excluir produto.", "danger")
        return redirect(url_for('index'))
    
@app.route('/excluir-imagem/<int:id>')
def excluir_imagem(id):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho, produto_id FROM imagens WHERE id=?", (id,))
            imagem = cursor.fetchone()
            if imagem:
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], imagem[0])
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")
                cursor.execute("DELETE FROM imagens WHERE id=?", (id,))
                conn.commit()
                flash("Imagem excluída com sucesso!", "success")
            else:
                flash("Imagem não encontrada.", "danger")
            return redirect(url_for('editar', id=imagem[1] if imagem else 0))
    except sqlite3.Error as e:
        logger.error(f"Erro ao excluir imagem: {e}")
        flash("Erro ao excluir imagem.", "danger")
        return redirect(url_for('index'))

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug)