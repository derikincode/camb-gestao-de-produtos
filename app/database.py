import sqlite3
import logging
import os
from .config import Config

logger = logging.getLogger(__name__)

def init_db():
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
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
                    descricao TEXT,
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
            if 'descricao' not in columns:
                cursor.execute('ALTER TABLE imagens ADD COLUMN descricao TEXT')
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        raise

def get_produtos(search=''):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
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
            return produtos_com_imagens
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return []

def get_produto_by_id(id):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id=?", (id,))
            produto = cursor.fetchone()
            cursor.execute("SELECT id, caminho, descricao FROM imagens WHERE produto_id=?", (id,))
            imagens = cursor.fetchall()
            return dict(produto) if produto else None, imagens
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar produto {id}: {e}")
        return None, []

def insert_produto(nome, codigo, descricao, altura, largura, comprimento, peso, marca):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE codigo=?", (codigo,))
            if cursor.fetchone():
                return None, "Código já existe."
            cursor.execute('''
                INSERT INTO produtos (nome, codigo, descricao, altura, largura, comprimento, peso, marca)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, codigo, descricao, altura, largura, comprimento, peso, marca))
            produto_id = cursor.lastrowid
            conn.commit()
            return produto_id, None
    except sqlite3.Error as e:
        logger.error(f"Erro ao cadastrar produto: {e}")
        return None, str(e)

def insert_imagem(produto_id, caminho, descricao):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO imagens (produto_id, caminho, descricao) VALUES (?, ?, ?)
            ''', (produto_id, caminho, descricao))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir imagem: {e}")
        raise

def update_produto(id, nome, codigo, descricao, altura, largura, comprimento, peso, marca):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE codigo=? AND id!=?", (codigo, id))
            if cursor.fetchone():
                return False, "Código já existe."
            cursor.execute('''
                UPDATE produtos SET nome=?, codigo=?, descricao=?, altura=?, largura=?, comprimento=?, peso=?, marca=? WHERE id=?
            ''', (nome, codigo, descricao, altura, largura, comprimento, peso, marca, id))
            conn.commit()
            return True, None
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar produto {id}: {e}")
        return False, str(e)

def update_imagem_descricao(id, descricao):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE imagens SET descricao=? WHERE id=?
            ''', (descricao, id))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar descrição da imagem {id}: {e}")
        raise

def delete_produto(id):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho FROM imagens WHERE produto_id=?", (id,))
            imagens = cursor.fetchall()
            for img in imagens:
                caminho = os.path.join(Config.UPLOAD_FOLDER, img[0])
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")
            cursor.execute("DELETE FROM imagens WHERE produto_id=?", (id,))
            cursor.execute("DELETE FROM produtos WHERE id=?", (id,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erro ao deletar produto {id}: {e}")
        raise

def delete_imagem(id):
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho, produto_id FROM imagens WHERE id=?", (id,))
            imagem = cursor.fetchone()
            if imagem:
                caminho = os.path.join(Config.UPLOAD_FOLDER, imagem[0])
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")
                cursor.execute("DELETE FROM imagens WHERE id=?", (id,))
                conn.commit()
                return imagem[1]
            return None
    except sqlite3.Error as e:
        logger.error(f"Erro ao excluir imagem {id}: {e}")
        raise