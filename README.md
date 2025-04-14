# CAMB - Sistema de Gestão de Produtos

Bem-vindo ao **CAMB**, um sistema web moderno e intuitivo para gerenciamento de produtos, desenvolvido com Flask e SQLite. O projeto foi criado para facilitar o cadastro, edição, visualização e exclusão de produtos, com suporte a imagens, validações robustas e uma interface amigável. Ideal para pequenas e médias empresas que precisam organizar seus estoques de forma eficiente.

---

## ✨ Funcionalidades

- **Cadastro de Produtos**: Registre produtos com informações detalhadas, como nome, código, descrição, dimensões (altura, largura, comprimento), peso e marca.
- **Upload de Imagens**: Adicione até 10 imagens por produto, com validação de formato, tamanho (máx. 5MB) e dimensões (máx. 2000x2000px). As imagens são comprimidas automaticamente para otimizar o armazenamento.
- **Busca Dinâmica**: Pesquise produtos por nome ou código diretamente na interface principal.
- **Edição e Exclusão**: Atualize informações de produtos ou remova-os com segurança, incluindo a exclusão de imagens associadas.
- **Visualização de Detalhes**: Veja os detalhes de cada produto em um modal com carrossel de imagens.
- **Interface Responsiva**: Design adaptável para desktops, tablets e smartphones, com botões flutuantes e layouts otimizados.
- **Validações Robustas**: Garante a integridade dos dados com verificações de campos obrigatórios, formatos numéricos e unicidade de códigos.
- **Segurança**: Proteção CSRF integrada e validação de extensões de arquivos para uploads.
- **Estilização Moderna**: Interface construída com Bootstrap 5, ícones Font Awesome e CSS personalizado para uma experiência visual agradável.

---

## 🛠 Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5, Font Awesome
- **Manipulação de Imagens**: Pillow (PIL)
- **Segurança**: Flask-WTF (CSRF Protection)
- **Outras Bibliotecas**: Werkzeug, UUID, OS

---

## 📷 Screenshots

### Página Inicial
![Página Inicial](screenshots/index.png)
*Lista de produtos com busca e ações rápidas.*

### Formulário de Cadastro/Edição
![Formulário](screenshots/form.png)
*Formulário intuitivo com validação em tempo real.*

### Modal de Detalhes
![Modal de Detalhes](screenshots/modal.png)
*Visualização detalhada com carrossel de imagens.*

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- Pip (gerenciador de pacotes do Python)
- Git (opcional, para clonar o repositório)

### Passos

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/derikoliveira/camb.git
   cd camb
