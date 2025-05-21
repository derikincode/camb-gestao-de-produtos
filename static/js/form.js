// Validação do formulário
(() => {
  "use strict";
  const form = document.getElementById("produtoForm");
  form.addEventListener(
    "submit",
    (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        const submitBtn = document.getElementById("submitBtn");
        submitBtn.disabled = true;
        submitBtn.classList.add("btn-loading");
        submitBtn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Salvando...';
      }
      form.classList.add("was-validated");
    },
    false
  );
})();

// Validação em tempo real
document.getElementById("codigo").addEventListener("input", function () {
  const codigo = this.value;
  const feedback = document.getElementById("codigoFeedback");
  if (codigo.length < 3) {
    this.classList.add("is-invalid");
    feedback.textContent = "O código deve ter pelo menos 3 caracteres.";
  } else {
    this.classList.remove("is-invalid");
    this.classList.add("is-valid");
  }
});

document.getElementById("nome").addEventListener("input", function () {
  const nome = this.value;
  const feedback = document.getElementById("nomeFeedback");
  if (nome.length < 1) {
    this.classList.add("is-invalid");
    feedback.textContent = "O nome é obrigatório.";
  } else {
    this.classList.remove("is-invalid");
    this.classList.add("is-valid");
  }
});

document.getElementById("marca").addEventListener("change", function () {
  const marca = this.value;
  const feedback = document.getElementById("marcaFeedback");
  if (!marca) {
    this.classList.add("is-invalid");
    feedback.textContent = "Selecione uma marca.";
  } else {
    this.classList.remove("is-invalid");
    this.classList.add("is-valid");
  }
});

document.getElementById("descricao").addEventListener("input", function () {
  const count = this.value.length;
  const counter = document.getElementById("descCount");
  counter.textContent = `${count}/300 caracteres`;
  if (count > 300) {
    this.classList.add("is-invalid");
    counter.classList.add("text-danger");
  } else {
    this.classList.remove("is-invalid");
    counter.classList.remove("text-danger");
  }
});

["altura", "largura", "comprimento", "peso"].forEach((field) => {
  document.getElementById(field).addEventListener("input", function () {
    const value = this.value;
    const feedback = document.getElementById(`${field}Feedback`);
    if (value && (isNaN(value) || value <= 0)) {
      this.classList.add("is-invalid");
      feedback.textContent = `Por favor, informe um ${field} válido maior que zero.`;
    } else {
      this.classList.remove("is-invalid");
      if (value) this.classList.add("is-valid");
    }
  });
});

// Visualização de imagens
function previewImagens(event) {
  const container = document.getElementById("preview-container");
  const fileCount = document.getElementById("fileCount");
  container.innerHTML = "";
  const files = event.target.files;

  if (files.length > 10) {
    alert("Você pode selecionar no máximo 10 imagens.");
    event.target.value = "";
    fileCount.textContent = "0/10 imagens selecionadas";
    return;
  }

  fileCount.textContent = `${files.length}/10 imagens selecionadas`;
  if (files.length >= 10) {
    event.target.disabled = true;
  }

  Array.from(files).forEach((file, index) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const wrapper = document.createElement("div");
      wrapper.className = "img-preview-wrapper position-relative";

      const img = document.createElement("img");
      img.src = e.target.result;
      img.className = "img-thumbnail";
      img.setAttribute("loading", "lazy");
      img.setAttribute("alt", "Pré-visualização da imagem");

      const descInput = document.createElement("textarea");
      descInput.className = "form-control mt-1 img-description";
      descInput.name = "fotos_desc[]";
      descInput.placeholder = "Descrição da imagem (máx. 300 caracteres)";
      descInput.maxLength = 300;
      descInput.rows = 1;

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className =
        "btn btn-sm btn-danger position-absolute top-0 end-0 remove-btn";
      removeBtn.innerHTML = "×";
      removeBtn.setAttribute("aria-label", `Remover imagem ${file.name}`);
      removeBtn.onclick = () => {
        wrapper.remove();
        const currentFiles = document.getElementById("fotos").files;
        const newFileList = new DataTransfer();
        Array.from(currentFiles)
          .filter((f) => f !== file)
          .forEach((f) => newFileList.items.add(f));
        document.getElementById("fotos").files = newFileList.files;
        fileCount.textContent = `${newFileList.files.length}/10 imagens selecionadas`;
        document.getElementById("fotos").disabled =
          newFileList.files.length >= 10;
      };

      wrapper.appendChild(img);
      wrapper.appendChild(descInput);
      wrapper.appendChild(removeBtn);
      container.appendChild(wrapper);
    };
    reader.readAsDataURL(file);
  });
}

// Drag-and-drop
function handleDrop(event) {
  event.preventDefault();
  event.currentTarget.classList.remove("drag-active");
  const files = event.dataTransfer.files;
  const input = document.getElementById("fotos");
  input.files = files;
  previewImagens({ target: { files } });
}

function handleDragEnter(event) {
  event.preventDefault();
  event.currentTarget.classList.add("drag-active");
}

function handleDragLeave(event) {
  event.preventDefault();
  event.currentTarget.classList.remove("drag-active");
}

// Fechar alertas automaticamente após 4 segundos
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.remove("show");
      alert.classList.add("fade");
      setTimeout(() => {
        alert.remove();
      }, 300);
    }, 4000);
  });
});
