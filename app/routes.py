from flask import render_template, request, redirect, url_for, flash
from .database import get_produtos, get_produto_by_id, insert_produto, insert_imagem, update_produto, update_imagem_descricao, delete_produto, delete_imagem
from .image_utils import allowed_file, validate_image_dimensions, compress_image
from .config import Config
import uuid
import os
import logging

logger = logging.getLogger(__name__)

def init_routes(app):
    @app.route('/')
    def index():
        search = request.args.get('search', '').strip()
        produtos = get_produtos(search)
        return render_template('index.html', produtos=produtos, search=search)

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

            produto_id, error = insert_produto(nome, codigo, descricao, altura, largura, comprimento, peso, marca)
            if error:
                flash(error, "danger")
                return redirect(url_for('cadastrar'))

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
                    caminho = os.path.join(Config.UPLOAD_FOLDER, filename)
                    try:
                        with open(caminho, 'wb') as f:
                            f.write(compressed_image.read())
                        insert_imagem(produto_id, filename, foto_desc.strip() if foto_desc else None)
                    except Exception as e:
                        logger.error(f"Erro ao salvar imagem: {e}")
                        flash("Erro ao salvar imagem.", "danger")

            flash("Produto cadastrado com sucesso!", "success")
            return redirect(url_for('index'))

        return render_template('form.html', produto=None, imagens=[])

    @app.route('/editar/<int:id>', methods=['GET', 'POST'])
    def editar(id):
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
                flash("Dimensões ou peso devem be números válidos.", "danger")
                return redirect(url_for('editar', id=id))

            success, error = update_produto(id, nome, codigo, descricao, altura, largura, comprimento, peso, marca)
            if not success:
                flash(error, "danger")
                return redirect(url_for('editar', id=id))

            for img_id, desc in existing_images_desc.items():
                desc = desc[0].strip() if desc and desc[0] else None
                update_imagem_descricao(img_id, desc)

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
                    caminho = os.path.join(Config.UPLOAD_FOLDER, filename)
                    try:
                        with open(caminho, 'wb') as f:
                            f.write(compressed_image.read())
                        insert_imagem(id, filename, foto_desc.strip() if foto_desc else None)
                    except Exception as e:
                        logger.error(f"Erro ao salvar imagem: {e}")
                        flash("Erro ao salvar imagem.", "danger")

            flash("Produto atualizado com sucesso!", "success")
            return redirect(url_for('index'))

        produto, imagens = get_produto_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "danger")
            return redirect(url_for('index'))
        return render_template('form.html', produto=produto, imagens=imagens)

    @app.route('/deletar/<int:id>')
    def deletar(id):
        try:
            delete_produto(id)
            flash("Produto excluído com sucesso!", "success")
        except Exception as e:
            flash("Erro ao excluir produto.", "danger")
        return redirect(url_for('index'))

    @app.route('/excluir-imagem/<int:id>')
    def excluir_imagem(id):
        produto_id = delete_imagem(id)
        if produto_id:
            flash("Imagem excluída com sucesso!", "success")
            return redirect(url_for('editar', id=produto_id))
        flash("Imagem não encontrada.", "danger")
        return redirect(url_for('index'))