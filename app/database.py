import sqlite3
import logging
import os
from .config import Config

logger = logging.getLogger(__name__)

def init_db():
    """
    Inicializa o banco de dados, cria tabelas e índices necessários,
    adiciona colunas caso não existam.
    """
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()

            # Criação das tabelas (se não existirem)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    codigo TEXT NOT NULL UNIQUE,
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

            # Criação de índice único para código (se não existir)
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_codigo ON produtos(codigo)')

            # Verifica e adiciona colunas extras se necessário
            def coluna_existe(tabela, coluna):
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = [col[1] for col in cursor.fetchall()]
                return coluna in colunas

            # Adiciona coluna 'peso' na tabela produtos se não existir
            if not coluna_existe('produtos', 'peso'):
                cursor.execute('ALTER TABLE produtos ADD COLUMN peso REAL')
                logger.info("Coluna 'peso' adicionada na tabela 'produtos'")

            # Adiciona coluna 'marca' na tabela produtos se não existir
            if not coluna_existe('produtos', 'marca'):
                cursor.execute('ALTER TABLE produtos ADD COLUMN marca TEXT')
                logger.info("Coluna 'marca' adicionada na tabela 'produtos'")

            # Adiciona coluna 'descricao' na tabela imagens se não existir
            if not coluna_existe('imagens', 'descricao'):
                cursor.execute('ALTER TABLE imagens ADD COLUMN descricao TEXT')
                logger.info("Coluna 'descricao' adicionada na tabela 'imagens'")

            conn.commit()
            logger.info("Banco de dados inicializado com sucesso.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        raise

def get_produtos(search=''):
    """
    Retorna lista de produtos com suas imagens associadas.
    """
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            base_query = """
                SELECT p.id, p.nome, p.codigo, p.descricao, p.altura, p.largura, p.comprimento, p.peso, p.marca,
                       GROUP_CONCAT(i.id) as imagem_ids,
                       GROUP_CONCAT(i.caminho) as imagem_caminhos,
                       GROUP_CONCAT(i.descricao) as imagem_descricoes
                FROM produtos p
                LEFT JOIN imagens i ON p.id = i.produto_id
            """

            params = []
            if search:
                base_query += " WHERE p.nome LIKE ? OR p.codigo LIKE ?"
                params.extend([f'%{search}%', f'%{search}%'])

            base_query += " GROUP BY p.id"

            cursor.execute(base_query, params)
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
    """
    Retorna produto pelo ID e suas imagens associadas.
    """
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
    """
    Insere um novo produto, retorna id ou mensagem de erro.
    """
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
            logger.info(f"Produto inserido com ID {produto_id} - código {codigo}")
            return produto_id, None
    except sqlite3.Error as e:
        logger.error(f"Erro ao cadastrar produto: {e}")
        return None, str(e)

def insert_imagem(produto_id, caminho, descricao):
    """
    Insere imagem vinculada a um produto.
    """
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO imagens (produto_id, caminho, descricao) VALUES (?, ?, ?)
            ''', (produto_id, caminho, descricao))

            conn.commit()
            logger.info(f"Imagem inserida para produto {produto_id} - caminho {caminho}")
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir imagem: {e}")
        raise

def update_produto(id, nome, codigo, descricao, altura, largura, comprimento, peso, marca):
    """
    Atualiza dados de um produto.
    """
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM produtos WHERE codigo=? AND id!=?", (codigo, id))
            if cursor.fetchone():
                return False, "Código já existe."

            cursor.execute('''
                UPDATE produtos SET nome=?, codigo=?, descricao=?, altura=?, largura=?, comprimento=?, peso=?, marca=?
                WHERE id=?
            ''', (nome, codigo, descricao, altura, largura, comprimento, peso, marca, id))

            conn.commit()
            logger.info(f"Produto atualizado ID {id}")
            return True, None
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar produto {id}: {e}")
        return False, str(e)

def update_imagem_descricao(id, descricao):
    """
    Atualiza a descrição de uma imagem.
    """
    try:
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute('UPDATE imagens SET descricao=? WHERE id=?', (descricao, id))
            conn.commit()
            logger.info(f"Descrição da imagem {id} atualizada.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao atualizar descrição da imagem {id}: {e}")
        raise

def delete_produto(id):
    """
    Exclui produto e suas imagens, removendo arquivos físicos.
    """
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
                        logger.info(f"Imagem removida: {caminho}")
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")

            cursor.execute("DELETE FROM imagens WHERE produto_id=?", (id,))
            cursor.execute("DELETE FROM produtos WHERE id=?", (id,))

            conn.commit()
            logger.info(f"Produto {id} e imagens excluídos.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao deletar produto {id}: {e}")
        raise

def delete_imagem(id):
    """
    Exclui imagem pelo ID, remove arquivo físico e retorna produto_id relacionado.
    """
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
                        logger.info(f"Imagem removida: {caminho}")
                    except OSError as e:
                        logger.error(f"Erro ao remover imagem {caminho}: {e}")

                cursor.execute("DELETE FROM imagens WHERE id=?", (id,))
                conn.commit()
                logger.info(f"Imagem {id} excluída do banco.")
                return imagem[1]

            return None
    except sqlite3.Error as e:
        logger.error(f"Erro ao excluir imagem {id}: {e}")
        raise
