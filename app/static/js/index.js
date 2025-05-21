document.addEventListener("DOMContentLoaded", function () {
    const botoes = document.querySelectorAll(".ver-detalhes");
    const nome = document.getElementById("modal-nome");
    const codigo = document.getElementById("modal-codigo");
    const marca = document.getElementById("modal-marca");
    const descricao = document.getElementById("modal-descricao");
    const altura = document.getElementById("modal-altura");
    const largura = document.getElementById("modal-largura");
    const comprimento = document.getElementById("modal-comprimento");
    const peso = document.getElementById("modal-peso");
    const carouselInner = document.getElementById("carousel-inner");
    const carouselCaption = document.getElementById("carousel-caption");

    // Define o caminho base para as imagens
    const baseImagePath = "{{ url_for('static', filename='uploads') | safe }}/";

    botoes.forEach((botao) => {
      botao.addEventListener("click", () => {
        codigo.textContent = botao.getAttribute("data-codigo") || "N/A";
        nome.textContent = botao.getAttribute("data-nome") || "N/A";
        marca.textContent = botao.getAttribute("data-marca") || "N/A";
        descricao.textContent = botao.getAttribute("data-descricao") || "N/A";
        altura.textContent = botao.getAttribute("data-altura") ? `${botao.getAttribute("data-altura")} cm` : "N/A";
        largura.textContent = botao.getAttribute("data-largura") ? `${botao.getAttribute("data-largura")} cm` : "N/A";
        comprimento.textContent = botao.getAttribute("data-comprimento") ? `${botao.getAttribute("data-comprimento")} cm` : "N/A";
        
        const pesoValor = botao.getAttribute("data-peso");
        peso.textContent = (pesoValor && pesoValor !== "None" && pesoValor !== "" && !isNaN(pesoValor)) ? `${pesoValor} kg` : "N/A";

        try {
          const imagensRaw = botao.getAttribute("data-imagens");
          const descricoesRaw = botao.getAttribute("data-imagens-desc");

          let imagens = [];
          let descricoes = [];
          if (imagensRaw) {
            try {
              imagens = JSON.parse(imagensRaw);
            } catch (parseError) {
              console.error("Erro ao parsear JSON de imagens:", parseError);
            }
          }
          if (descricoesRaw) {
            try {
              descricoes = JSON.parse(descricoesRaw);
            } catch (parseError) {
              console.error("Erro ao parsear JSON de descrições:", parseError);
            }
          }

          carouselInner.innerHTML = "";
          carouselCaption.innerHTML = "";
          if (!imagens || imagens.length === 0) {
            carouselInner.innerHTML = `<div class="carousel-item active text-center">
                <div class="no-image-placeholder">PRODUTO SEM IMAGEM</div>
              </div>`;
            carouselCaption.innerHTML = "Nenhuma descrição disponível";
          } else {
            imagens.forEach((img, index) => {
              const imageUrl = `${baseImagePath}${img}`;
              const desc = descricoes[index] && descricoes[index] !== "null" ? descricoes[index] : "Nenhuma descrição disponível";
              carouselInner.innerHTML += `<div class="carousel-item ${index === 0 ? "active" : ""}">
                <img src="${imageUrl}" class="d-block mx-auto" alt="Imagem do produto" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'no-image-placeholder\\'>ERRO AO CARREGAR IMAGEM</div>';">
              </div>`;
              if (index === 0) {
                carouselCaption.innerHTML = desc;
              }
            });
          }

          // Atualiza a descrição ao mudar o slide
          constcarousel = new bootstrap.Carousel(document.getElementById("carouselImagens"), { interval: true });
          document.getElementById("carouselImagens").addEventListener('slid.bs.carousel', function (event) {
            const activeIndex = event.to;
            const desc = descricoes[activeIndex] && descricoes[activeIndex] !== "null" ? descricoes[activeIndex] : "Nenhuma descrição disponível";
            carouselCaption.innerHTML = desc;
          });

        } catch (error) {
          console.error("Erro geral ao processar imagens:", error);
          carouselInner.innerHTML = `<div class="carousel-item active text-center">
              <div class="no-image-placeholder">PRODUTO SEM IMAGEM</div>
            </div>`;
          carouselCaption.innerHTML = "Nenhuma descrição disponível";
        }
      });
    });

    // Fecha alertas automaticamente após 4 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.classList.remove('show');
        alert.classList.add('fade');
        setTimeout(() => {
          alert.remove();
        }, 300);
      }, 4000);
    });
  });