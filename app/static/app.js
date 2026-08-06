const form = document.querySelector("#job-form");
const submitButton = document.querySelector("#submit-button");
const statusLabel = document.querySelector("#status-label");
const statusMessage = document.querySelector("#status-message");
const progressLabel = document.querySelector("#progress-label");
const progressBar = document.querySelector("#progress-bar");
const progressTrack = document.querySelector(".progress-track");
const resultPanel = document.querySelector("#result-panel");

const statusNames = {
  queued: "Aguardando",
  fetching_metadata: "Obtendo metadados",
  downloading: "Baixando áudio",
  transcribing: "Transcrevendo",
  generating_files: "Gerando arquivos",
  completed: "Concluído",
  failed: "Erro",
};

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
  document.querySelector("#transcript").textContent = job.transcript || "";

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
    link.href = `/api/jobs/${encodeURIComponent(job.job_id)}/files/${encodeURIComponent(filename)}`;
    link.textContent = labels[filename];
    link.className = "download-button";
    downloads.appendChild(link);
  });
  resultPanel.hidden = false;
}

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
    const response = await fetch(`/api/jobs/${encodeURIComponent(jobId)}`);
    if (!response.ok) throw new Error(await readError(response));
    const job = await response.json();
    updateStatus(job);
    if (job.status === "completed") {
      showResult(job);
      submitButton.disabled = false;
      return;
    }
    if (job.status === "failed") {
      submitButton.disabled = false;
      return;
    }
    window.setTimeout(() => pollJob(jobId), 1000);
  } catch (error) {
    statusLabel.textContent = "Erro";
    statusMessage.textContent = error.message;
    submitButton.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultPanel.hidden = true;
  submitButton.disabled = true;
  updateStatus({ status: "queued", progress: 0, message: "Criando job..." });

  const body = {
    url: form.url.value,
    model: form.model.value,
    language: form.language.value,
  };
  try {
    const response = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(await readError(response));
    const job = await response.json();
    updateStatus(job);
    pollJob(job.job_id);
  } catch (error) {
    statusLabel.textContent = "Erro";
    statusMessage.textContent = error.message;
    submitButton.disabled = false;
  }
});
