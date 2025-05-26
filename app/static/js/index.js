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
  const carouselElement = document.getElementById("carouselImagens");

  const baseImagePath = "/static/uploads/";

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

      // Processa as imagens e descrições do carousel
      let imagens = [];
      let descricoes = [];

      try {
        const imagensRaw = botao.getAttribute("data-imagens");
        const descricoesRaw = botao.getAttribute("data-imagens-desc");

        if (imagensRaw && imagensRaw.trim() !== "") {
          imagens = JSON.parse(imagensRaw);
          if (!Array.isArray(imagens)) imagens = [];
        }

        if (descricoesRaw && descricoesRaw.trim() !== "") {
          descricoes = JSON.parse(descricoesRaw);
          if (!Array.isArray(descricoes)) descricoes = [];
        }
      } catch (parseError) {
        console.error("Erro ao parsear JSON de imagens ou descrições:", parseError);
        imagens = [];
        descricoes = [];
      }

      // Limpa conteúdo anterior do carousel
      carouselInner.innerHTML = "";
      carouselCaption.textContent = "";

      if (imagens.length === 0) {
        carouselInner.innerHTML = `
          <div class="carousel-item active text-center">
            <div class="no-image-placeholder">PRODUTO SEM IMAGEM</div>
          </div>`;
        carouselCaption.textContent = "Nenhuma descrição disponível";
      } else {
        const fragment = document.createDocumentFragment();

        imagens.forEach((img, index) => {
          const itemDiv = document.createElement("div");
          itemDiv.className = `carousel-item${index === 0 ? " active" : ""}`;

          const image = document.createElement("img");
          image.src = `${baseImagePath}${img}`;
          image.className = "d-block mx-auto";
          image.alt = "Imagem do produto";

          image.onerror = function () {
            this.onerror = null;
            this.parentElement.innerHTML = '<div class="no-image-placeholder">ERRO AO CARREGAR IMAGEM</div>';
          };

          itemDiv.appendChild(image);
          fragment.appendChild(itemDiv);

          if (index === 0) {
            const desc = descricoes[index] && descricoes[index] !== "null" ? descricoes[index] : "Nenhuma descrição disponível";
            carouselCaption.textContent = desc;
          }
        });

        carouselInner.appendChild(fragment);
      }

      if (carouselElement) {
        if (carouselElement._carouselInstance) {
          carouselElement._carouselInstance.dispose();
        }

        carouselElement._carouselInstance = new bootstrap.Carousel(carouselElement, { interval: true });

        carouselElement.addEventListener('slid.bs.carousel', function (event) {
          const activeIndex = event.to;
          const desc = descricoes[activeIndex] && descricoes[activeIndex] !== "null" ? descricoes[activeIndex] : "Nenhuma descrição disponível";
          carouselCaption.textContent = desc;
        });
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
