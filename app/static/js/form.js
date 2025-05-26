(() => {
  "use strict";

  // Cache dos elementos usados com frequência
  const form = document.getElementById("produtoForm");
  const submitBtn = document.getElementById("submitBtn");
  const fotosInput = document.getElementById("fotos");
  const previewContainer = document.getElementById("preview-container");
  const fileCount = document.getElementById("fileCount");

  // Limite máximo de imagens
  const MAX_IMAGES = 10;

  // Função para mostrar loading no botão submit
  function showLoading() {
    submitBtn.disabled = true;
    submitBtn.classList.add("btn-loading");
    submitBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Salvando...';
  }

  // Função para resetar estados do botão submit
  function resetSubmitBtn() {
    submitBtn.disabled = false;
    submitBtn.classList.remove("btn-loading");
    submitBtn.textContent = "Salvar";
  }

  // Validação geral ao submeter o formulário
  form.addEventListener("submit", (event) => {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
      resetSubmitBtn();
    } else {
      showLoading();
    }
    form.classList.add("was-validated");
  });

  // Validações específicas com feedback customizado
  const validations = {
    codigo(input) {
      const feedback = document.getElementById("codigoFeedback");
      if (input.value.trim().length < 3) {
        setInvalid(input, feedback, "O código deve ter pelo menos 3 caracteres.");
      } else {
        setValid(input, feedback);
      }
    },
    nome(input) {
      const feedback = document.getElementById("nomeFeedback");
      if (input.value.trim().length === 0) {
        setInvalid(input, feedback, "O nome é obrigatório.");
      } else {
        setValid(input, feedback);
      }
    },
    marca(input) {
      const feedback = document.getElementById("marcaFeedback");
      if (!input.value) {
        setInvalid(input, feedback, "Selecione uma marca.");
      } else {
        setValid(input, feedback);
      }
    },
    descricao(input) {
      const counter = document.getElementById("descCount");
      const count = input.value.length;
      counter.textContent = `${count}/300 caracteres`;
      if (count > 300) {
        input.classList.add("is-invalid");
        counter.classList.add("text-danger");
      } else {
        input.classList.remove("is-invalid");
        counter.classList.remove("text-danger");
      }
    },
    numeric(input) {
      const field = input.id;
      const feedback = document.getElementById(`${field}Feedback`);
      const value = input.value.trim();
      if (value && (isNaN(value) || Number(value) <= 0)) {
        setInvalid(input, feedback, `Por favor, informe um ${field} válido maior que zero.`);
      } else {
        setValid(input, feedback, value !== "");
      }
    }
  };

  // Helpers para aplicar classes de validação
  function setInvalid(input, feedback, message) {
    input.classList.add("is-invalid");
    input.classList.remove("is-valid");
    if (feedback) feedback.textContent = message;
  }

  function setValid(input, feedback, addValidClass = true) {
    input.classList.remove("is-invalid");
    if (addValidClass) input.classList.add("is-valid");
    else input.classList.remove("is-valid");
    if (feedback) feedback.textContent = "";
  }

  // Aplicar validações em tempo real
  document.getElementById("codigo").addEventListener("input", (e) => validations.codigo(e.target));
  document.getElementById("nome").addEventListener("input", (e) => validations.nome(e.target));
  document.getElementById("marca").addEventListener("change", (e) => validations.marca(e.target));
  document.getElementById("descricao").addEventListener("input", (e) => validations.descricao(e.target));

  ["altura", "largura", "comprimento", "peso"].forEach((field) => {
    document.getElementById(field).addEventListener("input", (e) => validations.numeric(e.target));
  });

  // --- Manipulação de imagens ---

  // Atualiza o contador e botão de seleção de imagens
  function updateFileCount(files) {
    fileCount.textContent = `${files.length}/${MAX_IMAGES} imagens selecionadas`;
    fotosInput.disabled = files.length >= MAX_IMAGES;
  }

  // Função para criar preview da imagem com descrição e botão remover
  function createImagePreview(file) {
    const wrapper = document.createElement("div");
    wrapper.className = "img-preview-wrapper position-relative";

    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.className = "img-thumbnail";
    img.loading = "lazy";
    img.alt = `Pré-visualização da imagem: ${file.name}`;

    const descInput = document.createElement("textarea");
    descInput.className = "form-control mt-1 img-description";
    descInput.name = "fotos_desc[]";
    descInput.placeholder = "Descrição da imagem (máx. 300 caracteres)";
    descInput.maxLength = 300;
    descInput.rows = 1;

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-sm btn-danger position-absolute top-0 end-0 remove-btn";
    removeBtn.setAttribute("aria-label", `Remover imagem ${file.name}`);
    removeBtn.innerHTML = "×";

    // Remove imagem e atualiza input
    removeBtn.addEventListener("click", () => {
      wrapper.remove();
      removeFileFromInput(file);
    });

    wrapper.append(img, descInput, removeBtn);
    return wrapper;
  }

  // Remove arquivo do input "fotos"
  function removeFileFromInput(fileToRemove) {
    const dt = new DataTransfer();
    Array.from(fotosInput.files)
      .filter((file) => file !== fileToRemove)
      .forEach((file) => dt.items.add(file));
    fotosInput.files = dt.files;
    updateFileCount(fotosInput.files);
  }

  // Cria previews para todos os arquivos selecionados
  function previewImagens(event) {
    const files = event.target.files;
    previewContainer.innerHTML = "";

    if (files.length > MAX_IMAGES) {
      alert(`Você pode selecionar no máximo ${MAX_IMAGES} imagens.`);
      fotosInput.value = "";
      updateFileCount([]);
      return;
    }

    updateFileCount(files);

    Array.from(files).forEach((file) => {
      const preview = createImagePreview(file);
      previewContainer.appendChild(preview);
    });
  }

  // Eventos drag-and-drop
  function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove("drag-active");

    // Adiciona arquivos ao input mantendo os anteriores (se quiser substituir, é só trocar a lógica)
    const droppedFiles = Array.from(event.dataTransfer.files);
    const currentFiles = Array.from(fotosInput.files);
    const allFiles = [...currentFiles, ...droppedFiles].slice(0, MAX_IMAGES);

    const dt = new DataTransfer();
    allFiles.forEach((file) => dt.items.add(file));
    fotosInput.files = dt.files;

    previewImagens({ target: { files: fotosInput.files } });
  }

  function handleDragEnter(event) {
    event.preventDefault();
    event.currentTarget.classList.add("drag-active");
  }

  function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove("drag-active");
  }

  // Attach eventos drag-drop ao container das imagens, se existir
  const dropZone = document.getElementById("drop-zone");
  if (dropZone) {
    dropZone.addEventListener("dragenter", handleDragEnter);
    dropZone.addEventListener("dragleave", handleDragLeave);
    dropZone.addEventListener("dragover", (e) => e.preventDefault());
    dropZone.addEventListener("drop", handleDrop);
  }

  // Atualiza preview ao escolher arquivos pelo input
  fotosInput.addEventListener("change", previewImagens);

  // Fechar alertas automaticamente após 4 segundos
  document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach((alert) => {
      setTimeout(() => {
        alert.classList.remove("show");
        alert.classList.add("fade");
        setTimeout(() => alert.remove(), 300);
      }, 4000);
    });
  });
})();
