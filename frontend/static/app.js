const form = document.querySelector("#job-form");
const submitButton = document.querySelector("#submit-button");
const cancelButton = document.querySelector("#cancel-button");
const statusLabel = document.querySelector("#status-label");
const statusMessage = document.querySelector("#status-message");
const progressLabel = document.querySelector("#progress-label");
const progressBar = document.querySelector("#progress-bar");
const progressTrack = document.querySelector(".progress-track");
const resultPanel = document.querySelector("#result-panel");
const transcript = document.querySelector("#transcript");
const copyButton = document.querySelector("#copy-transcript");
const copyLabel = copyButton.querySelector(".copy-label");
let pollFailureCount = 0;
let activeJobId = null;
let pollTimer = null;

const statusNames = {
  queued: "Aguardando",
  fetching_metadata: "Obtendo metadados",
  downloading: "Baixando áudio",
  transcribing: "Transcrevendo",
  generating_files: "Gerando arquivos",
  completed: "Concluído",
  failed: "Erro",
  cancelled: "Cancelado",
};

const terminalStatuses = new Set(["completed", "failed", "cancelled"]);

function clearPollTimer() {
  if (pollTimer) {
    window.clearTimeout(pollTimer);
    pollTimer = null;
  }
}

function setCancelVisible(visible) {
  cancelButton.hidden = !visible;
  cancelButton.disabled = !visible;
}

function updateStatus(job) {
  const progress = Math.max(0, Math.min(100, job.progress || 0));
  statusLabel.textContent = statusNames[job.status] || job.status;
  statusMessage.textContent = job.message;
  progressLabel.textContent = `${progress}%`;
  progressBar.style.width = `${progress}%`;
  progressTrack.setAttribute("aria-valuenow", String(progress));
}

function formatDuration(totalSeconds) {
  if (!Number.isFinite(totalSeconds)) return "Não informada";
  const seconds = Math.round(totalSeconds);
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const rest = seconds % 60;
  return hours
    ? `${hours}:${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`
    : `${minutes}:${String(rest).padStart(2, "0")}`;
}

function showResult(job) {
  const metadata = job.metadata;
  document.querySelector("#video-title").textContent = metadata.title;
  document.querySelector("#video-channel").textContent = metadata.channel;
  document.querySelector("#video-duration").textContent = formatDuration(metadata.duration_seconds);
  document.querySelector("#video-language").textContent = metadata.detected_language || "Não detectado";
  transcript.textContent = job.transcript || "";
  copyButton.disabled = !job.transcript;
  copyLabel.textContent = "Copiar";
  copyButton.setAttribute("aria-label", "Copiar transcrição completa");

  const labels = {
    "audio.mp3": "Download MP3",
    "transcript.txt": "Download TXT",
    "transcript.srt": "Download SRT",
    "metadata.json": "Download JSON",
  };
  const downloads = document.querySelector("#downloads");
  downloads.replaceChildren();
  job.artifacts.forEach((filename) => {
    const link = document.createElement("a");
    link.href = `/api/v1/jobs/${encodeURIComponent(job.job_id)}/files/${encodeURIComponent(filename)}`;
    link.textContent = labels[filename];
    link.className = "download-button";
    downloads.appendChild(link);
  });
  resultPanel.hidden = false;
}

function fallbackCopy(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.setAttribute("readonly", "");
  textArea.style.position = "fixed";
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.width = "1px";
  textArea.style.height = "1px";
  textArea.style.padding = "0";
  textArea.style.border = "0";
  textArea.style.fontSize = "16px";
  textArea.style.opacity = "0.01";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  textArea.setSelectionRange(0, textArea.value.length);
  const copied = document.execCommand("copy");
  textArea.remove();
  if (!copied) throw new Error("Falha ao copiar.");
}

async function copyTranscript() {
  const text = transcript.textContent.trim();
  if (!text) return;

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      fallbackCopy(text);
    }
    copyLabel.textContent = "Copiado!";
    copyButton.setAttribute("aria-label", "Transcrição copiada");
  } catch {
    copyLabel.textContent = "Não copiou";
    copyButton.setAttribute("aria-label", "Não foi possível copiar a transcrição");
  }
  window.setTimeout(() => {
    copyLabel.textContent = "Copiar";
    copyButton.setAttribute("aria-label", "Copiar transcrição completa");
  }, 2000);
}

copyButton.addEventListener("click", copyTranscript);

async function readError(response) {
  try {
    const data = await response.json();
    const detail = data.detail;
    if (Array.isArray(detail)) return detail[0]?.msg?.replace(/^Value error, /, "") || "Dados inválidos.";
    return detail || "Ocorreu um erro inesperado.";
  } catch {
    return "O servidor não respondeu como esperado.";
  }
}

async function pollJob(jobId) {
  try {
    const response = await fetch(`/api/v1/jobs/${encodeURIComponent(jobId)}`, {
      credentials: "same-origin",
    });
    if (response.status === 404) {
      statusLabel.textContent = "Job indisponível";
      statusMessage.textContent =
        "Este job não existe mais. O servidor pode ter reiniciado; inicie um novo processamento.";
      submitButton.disabled = false;
      setCancelVisible(false);
      activeJobId = null;
      return;
    }
    if (!response.ok) throw new Error(await readError(response));
    const job = await response.json();
    pollFailureCount = 0;
    updateStatus(job);
    if (terminalStatuses.has(job.status)) {
      if (job.status === "completed") showResult(job);
      submitButton.disabled = false;
      setCancelVisible(false);
      activeJobId = null;
      return;
    }
    setCancelVisible(true);
    pollTimer = window.setTimeout(() => pollJob(jobId), 1000);
  } catch (error) {
    pollFailureCount += 1;
    const retryDelay = Math.min(1000 * pollFailureCount, 5000);
    statusLabel.textContent = "Reconectando";
    statusMessage.textContent = navigator.onLine
      ? `Não foi possível atualizar o status. Nova tentativa automática em ${retryDelay / 1000}s; o processamento continua no servidor.`
      : "O dispositivo está sem conexão. O acompanhamento será retomado automaticamente.";
    pollTimer = window.setTimeout(() => pollJob(jobId), retryDelay);
  }
}

cancelButton.addEventListener("click", async () => {
  if (!activeJobId) return;
  cancelButton.disabled = true;
  try {
    const response = await fetch(`/api/v1/jobs/${encodeURIComponent(activeJobId)}/cancel`, {
      method: "POST",
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error(await readError(response));
    const job = await response.json();
    updateStatus(job);
  } catch (error) {
    statusMessage.textContent = error.message;
    cancelButton.disabled = false;
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearPollTimer();
  resultPanel.hidden = true;
  pollFailureCount = 0;
  submitButton.disabled = true;
  setCancelVisible(false);
  updateStatus({ status: "queued", progress: 0, message: "Criando job..." });

  const body = {
    url: form.url.value,
    model: form.model.value,
    language: form.language.value,
    force: Boolean(form.force.checked),
  };
  try {
    const response = await fetch("/api/v1/jobs", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(await readError(response));
    const job = await response.json();
    activeJobId = job.job_id;
    updateStatus(job);
    setCancelVisible(true);
    pollJob(job.job_id);
  } catch (error) {
    statusLabel.textContent = "Erro";
    statusMessage.textContent = error.message;
    submitButton.disabled = false;
    setCancelVisible(false);
    activeJobId = null;
  }
});
