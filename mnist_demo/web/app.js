document.addEventListener("DOMContentLoaded", () => {
  // Elementos da interface
  const statusBadge = document.getElementById("status-badge");
  const alertaBox = document.getElementById("mensagem-alerta");
  const placeholderBox = document.getElementById("resultado-container");
  const detalhesBox = document.getElementById("resultado-detalhes");

  const canvas = document.getElementById("paint-canvas");
  const ctx = canvas.getContext("2d");
  const btnLimpar = document.getElementById("btn-limpar");
  const btnPredizerCanvas = document.getElementById("btn-predizer-canvas");

  const fileInput = document.getElementById("file-input");
  const dropzone = document.getElementById("dropzone");
  const uploadPreview = document.getElementById("upload-preview");
  const fundoSelect = document.getElementById("fundo-select");
  const btnPredizerUpload = document.getElementById("btn-predizer-upload");

  const valorPredito = document.getElementById("valor-predito");
  const valorConfianca = document.getElementById("valor-confianca");
  const valorTemperatura = document.getElementById("valor-temperatura");
  const barrasProbabilidades = document.getElementById("barras-probabilidades");

  const etapaOriginal = document.getElementById("etapa-original");
  const etapaCinza = document.getElementById("etapa-cinza");
  const etapaContraste = document.getElementById("etapa-contraste");
  const etapaTraco = document.getElementById("etapa-traco");
  const etapaEntrada = document.getElementById("etapa-entrada");

  let uploadBase64 = null;
  let desenhando = false;
  let canvasTemTraco = false;
  let espessuraTraco = 24; // Padrão 24px (densidade compatível com MNIST)

  // 1. Inicialização do Canvas
  function resetarCanvas() {
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "#111827";
    ctx.lineWidth = espessuraTraco;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    canvasTemTraco = false;
  }
  resetarCanvas();

  // Configuração dos botões de espessura do pincel
  const btnBrushes = document.querySelectorAll(".btn-brush");
  btnBrushes.forEach(btn => {
    btn.addEventListener("click", () => {
      btnBrushes.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      espessuraTraco = parseInt(btn.dataset.size, 10) || 24;
      ctx.lineWidth = espessuraTraco;
    });
  });

  function iniciarTraco(e) {
    desenhando = true;
    canvasTemTraco = true;
    const { x, y } = obterPosicao(e);
    // Garante que toques pontuais também criem um ponto sólido
    ctx.beginPath();
    ctx.arc(x, y, espessuraTraco / 2, 0, Math.PI * 2);
    ctx.fillStyle = "#111827";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(x, y);
  }

  function moverTraco(e) {
    if (!desenhando) return;
    const { x, y } = obterPosicao(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  }

  function finalizarTraco() {
    if (!desenhando) return;
    desenhando = false;
    ctx.closePath();
  }

  function obterPosicao(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  }

  canvas.addEventListener("pointerdown", iniciarTraco);
  canvas.addEventListener("pointermove", moverTraco);
  window.addEventListener("pointerup", finalizarTraco);
  canvas.addEventListener("pointercancel", finalizarTraco);

  btnLimpar.addEventListener("click", () => {
    resetarCanvas();
    ocultarAlerta();
  });

  // 2. Abas de Navegação
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
      ocultarAlerta();
    });
  });

  // 3. Upload de Arquivos
  function carregarArquivo(file) {
    if (!file) return;
    if (!file.type.match("image/(png|jpeg|webp)")) {
      exibirAlerta("Formato inválido. Envie um arquivo PNG, JPEG ou WebP.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadBase64 = e.target.result;
      uploadPreview.src = uploadBase64;
      uploadPreview.classList.remove("hidden");
      btnPredizerUpload.disabled = false;
      ocultarAlerta();
    };
    reader.readAsDataURL(file);
  }

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      carregarArquivo(e.target.files[0]);
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--primary)";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "var(--border-color)";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--border-color)";
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      carregarArquivo(e.dataTransfer.files[0]);
    }
  });

  // 4. Atalhos para Exemplos do Estudo
  document.querySelectorAll(".btn-exemplo").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      ocultarAlerta();
      try {
        const resp = await fetch(`/api/exemplo?id=${encodeURIComponent(id)}`);
        if (!resp.ok) throw new Error("Exemplo não localizado.");
        const dados = await resp.json();
        executarPredicao(dados.imagem, "claro");
      } catch (err) {
        exibirAlerta(`Falha ao carregar exemplo: ${err.message}`);
      }
    });
  });

  // 5. Envio para Predição
  btnPredizerCanvas.addEventListener("click", () => {
    if (!canvasTemTraco) {
      exibirAlerta("Desenhe um dígito no quadro antes de solicitar a classificação.");
      return;
    }
    const dataUrl = canvas.toDataURL("image/png");
    executarPredicao(dataUrl, "claro");
  });

  btnPredizerUpload.addEventListener("click", () => {
    if (!uploadBase64) {
      exibirAlerta("Selecione ou arraste uma foto antes de prosseguir.");
      return;
    }
    const fundo = fundoSelect.value;
    executarPredicao(uploadBase64, fundo);
  });

  async function executarPredicao(imagemBase64, fundo) {
    ocultarAlerta();
    statusBadge.textContent = "Processando...";
    statusBadge.className = "badge badge-info";

    try {
      const resp = await fetch("/api/predizer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imagem: imagemBase64, fundo: fundo })
      });

      const res = await resp.json();
      if (!resp.ok) {
        throw new Error(res.erro || "Falha na inferência.");
      }

      exibirResultado(res);
      statusBadge.textContent = "CNN Pronta";
      statusBadge.className = "badge badge-success";
    } catch (err) {
      exibirAlerta(err.message);
      statusBadge.textContent = "Erro";
      statusBadge.className = "badge badge-error";
    }
  }

  // 6. Renderização dos Resultados
  function exibirResultado(dados) {
    placeholderBox.classList.add("hidden");
    detalhesBox.classList.remove("hidden");

    valorPredito.textContent = dados.previsto;
    valorConfianca.textContent = `${(dados.confianca * 100).toFixed(1)}%`;
    valorTemperatura.textContent = `Temperatura T = ${dados.temperatura.toFixed(3)}`;

    // Renderizar as 10 barras de probabilidades
    barrasProbabilidades.innerHTML = "";
    dados.probabilidades.forEach((prob, digito) => {
      const porcentagem = (prob * 100).toFixed(1);
      const isVencedor = digito === dados.previsto;

      const item = document.createElement("div");
      item.className = `barra-item ${isVencedor ? "vencedor" : ""}`;
      item.innerHTML = `
        <span class="barra-digito">${digito}</span>
        <div class="barra-trilho">
          <div class="barra-preenchimento" style="width: ${porcentagem}%"></div>
        </div>
        <span class="barra-porcentagem">${porcentagem}%</span>
      `;
      barrasProbabilidades.appendChild(item);
    });

    // Renderizar as 5 etapas visuais
    if (dados.etapas) {
      etapaOriginal.src = dados.etapas.original || "";
      etapaCinza.src = dados.etapas.cinza || "";
      etapaContraste.src = dados.etapas.contraste || "";
      etapaTraco.src = dados.etapas.traco || "";
      etapaEntrada.src = dados.etapas.entrada || "";
    }
  }

  function exibirAlerta(msg) {
    alertaBox.textContent = msg;
    alertaBox.className = "alert alert-error";
    alertaBox.classList.remove("hidden");
  }

  function ocultarAlerta() {
    alertaBox.classList.add("hidden");
  }

  // 7. Checagem inicial do modelo
  fetch("/api/estado")
    .then(r => r.json())
    .then(dados => {
      if (dados.modelo_disponivel) {
        statusBadge.textContent = "CNN Pronta";
        statusBadge.className = "badge badge-success";
      } else {
        statusBadge.textContent = "Modelo Ausente";
        statusBadge.className = "badge badge-error";
        exibirAlerta("CNN ou calibração não encontradas. Execute o notebook para gerar os artefatos.");
      }
    })
    .catch(() => {
      statusBadge.textContent = "Servidor Offline";
      statusBadge.className = "badge badge-error";
    });
});
