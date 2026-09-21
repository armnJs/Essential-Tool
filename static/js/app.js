document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const conversionPanel = document.getElementById("conversionPanel");
  const fileName = document.getElementById("fileName");
  const fileMeta = document.getElementById("fileMeta");
  const fileIconBadge = document.getElementById("fileIconBadge");
  const removeFileBtn = document.getElementById("removeFileBtn");
  const formatPills = document.getElementById("formatPills");
  const optionsGrid = document.getElementById("optionsGrid");
  const imageOptions = document.getElementById("imageOptions");
  const sqlOptions = document.getElementById("sqlOptions");
  const ttsOptions = document.getElementById("ttsOptions");
  const qualityInput = document.getElementById("qualityInput");
  const qualityVal = document.getElementById("qualityVal");
  const grayscaleInput = document.getElementById("grayscaleInput");
  const resizeInput = document.getElementById("resizeInput");
  const tableNameInput = document.getElementById("tableNameInput");
  const langInput = document.getElementById("langInput");
  const convertBtn = document.getElementById("convertBtn");
  const convertBtnText = document.getElementById("convertBtnText");
  const spinner = document.getElementById("spinner");
  const resultCard = document.getElementById("resultCard");
  const resultMeta = document.getElementById("resultMeta");
  const downloadBtn = document.getElementById("downloadBtn");
  const convertAnotherBtn = document.getElementById("convertAnotherBtn");
  const errorBanner = document.getElementById("errorBanner");
  const errorMsg = document.getElementById("errorMsg");
  const closeErrorBtn = document.getElementById("closeErrorBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const dragQuoteBadge = document.getElementById("dragQuoteBadge");

  // State Variables
  let currentFile = null;
  let selectedTargetFormat = null;
  let downloadUrl = null;

  // Creative Drag Quotes Catalog
  const DRAG_QUOTES = [
    "🔥 Drop it like a hot pan!",
    "🚀 Drop it like it's hot! We'll handle the rest!",
    "🍳 Careful! Fresh file incoming, hot off the grid!",
    "⚡ Release the file! Unleash conversion magic!",
    "🎯 Target locked! Drop your file right here!",
    "🧲 Magnet activated! Feed me your document!",
    "🪄 Drop it down and watch it transform!"
  ];

  // Initialize Theme
  const savedTheme = localStorage.getItem("omni_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  window.toggleTheme = function() {
    const activeTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = activeTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("omni_theme", newTheme);
    updateThemeIcon(newTheme);
  };

  function updateThemeIcon(theme) {
    const box = document.getElementById("themeIconBox") || themeToggleBtn;
    if (box) {
      const iconName = theme === "dark" ? "moon" : "sun";
      box.innerHTML = `<i data-feather="${iconName}"></i>`;
      box.setAttribute("title", theme === "dark" ? "Dark Mode (Click for Light Mode)" : "Light Mode (Click for Dark Mode)");
      if (typeof feather !== "undefined") {
        feather.replace();
      }
    }
  }

  // Quality Slider Value Update
  if (qualityInput) {
    qualityInput.addEventListener("input", (e) => {
      if (qualityVal) qualityVal.textContent = e.target.value;
    });
  }

  // Drag & Drop Handlers
  if (dropzone) {
    dropzone.addEventListener("click", (e) => {
      if (e.target.closest("#fileInput") || e.target.closest("#removeFileBtn") || e.target.closest(".browse-btn")) return;
      if (fileInput) fileInput.click();
    });

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      if (!dropzone.classList.contains("dragover")) {
        dropzone.classList.add("dragover");
        const randomQuote = DRAG_QUOTES[Math.floor(Math.random() * DRAG_QUOTES.length)];
        if (dragQuoteBadge) {
          dragQuoteBadge.textContent = randomQuote;
          dragQuoteBadge.style.display = "inline-block";
        }
      }
    });

    dropzone.addEventListener("dragleave", (e) => {
      if (e.relatedTarget && !dropzone.contains(e.relatedTarget)) {
        dropzone.classList.remove("dragover");
        if (dragQuoteBadge) dragQuoteBadge.style.display = "none";
      }
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (dragQuoteBadge) dragQuoteBadge.style.display = "none";
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelected(e.dataTransfer.files[0]);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener("click", (e) => e.stopPropagation());
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  if (removeFileBtn) removeFileBtn.addEventListener("click", resetFileSelection);
  if (convertAnotherBtn) convertAnotherBtn.addEventListener("click", resetFileSelection);
  if (closeErrorBtn) closeErrorBtn.addEventListener("click", hideError);

  // File Selection
  async function handleFileSelected(file) {
    currentFile = file;
    hideError();

    const ext = getFileExtension(file.name);
    if (fileName) fileName.textContent = file.name;
    if (fileMeta) fileMeta.textContent = `${formatBytes(file.size)} • .${ext.toUpperCase()}`;
    if (fileIconBadge) fileIconBadge.textContent = ext.substring(0, 4).toUpperCase();

    if (dropzone) dropzone.classList.add("hidden");
    if (resultCard) resultCard.classList.add("hidden");
    if (conversionPanel) conversionPanel.classList.remove("hidden");

    await loadTargetFormats(ext);
  }

  // Load Compatible Target Formats from API
  async function loadTargetFormats(srcExt) {
    if (!formatPills) return;
    formatPills.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">Loading available targets...</span>';
    selectedTargetFormat = null;
    if (convertBtn) convertBtn.disabled = true;

    try {
      const resp = await fetch(`/api/formats?src=${encodeURIComponent(srcExt)}`);
      const data = await resp.json();
      const targets = data.allowed_targets || ["pdf", "zip", "txt"];

      formatPills.innerHTML = "";
      targets.forEach((fmt, index) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `format-pill ${index === 0 ? 'active' : ''}`;
        btn.textContent = fmt;

        btn.addEventListener("click", () => {
          formatPills.querySelectorAll(".format-pill").forEach(p => p.classList.remove("active"));
          btn.classList.add("active");
          selectedTargetFormat = fmt;
          if (convertBtn) convertBtn.disabled = false;
          updateOptionsVisibility(fmt);
        });

        formatPills.appendChild(btn);

        if (index === 0) {
          btn.click();
        }
      });
    } catch (err) {
      console.error("Format load error:", err);
      renderFallbackTargets();
    }
  }

  function renderFallbackTargets() {
    if (!formatPills) return;
    const targets = ["pdf", "png", "jpg", "txt", "zip"];
    formatPills.innerHTML = "";
    targets.forEach((fmt, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `format-pill ${index === 0 ? 'active' : ''}`;
      btn.textContent = fmt;

      btn.addEventListener("click", () => {
        formatPills.querySelectorAll(".format-pill").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        selectedTargetFormat = fmt;
        if (convertBtn) convertBtn.disabled = false;
        updateOptionsVisibility(fmt);
      });

      formatPills.appendChild(btn);
      if (index === 0) btn.click();
    });
  }

  // Toggle Options Panel Visibility
  function updateOptionsVisibility(targetFormat) {
    hideOptionGroups();
    let hasOptions = false;
    const targetClean = targetFormat.toLowerCase();

    if (["jpg", "jpeg", "png", "webp", "bmp", "ico", "tiff"].includes(targetClean)) {
      if (imageOptions) imageOptions.classList.remove("hidden");
      hasOptions = true;
    }

    if (targetClean === "sql") {
      if (sqlOptions) sqlOptions.classList.remove("hidden");
      hasOptions = true;
    }

    if (["mp3", "wav"].includes(targetClean)) {
      if (ttsOptions) ttsOptions.classList.remove("hidden");
      hasOptions = true;
    }

    if (optionsGrid) {
      if (hasOptions) {
        optionsGrid.classList.remove("hidden");
      } else {
        optionsGrid.classList.add("hidden");
      }
    }
  }

  function hideOptionGroups() {
    if (imageOptions) imageOptions.classList.add("hidden");
    if (sqlOptions) sqlOptions.classList.add("hidden");
    if (ttsOptions) ttsOptions.classList.add("hidden");
  }

  // Convert File Action Handler
  if (convertBtn) {
    convertBtn.addEventListener("click", async () => {
      if (!currentFile || !selectedTargetFormat) {
        showError("Please select a file and target format.");
        return;
      }

      hideError();
      setLoading(true);

      const formData = new FormData();
      formData.append("file", currentFile);
      formData.append("target_format", selectedTargetFormat);

      // Build options dictionary
      const optionsObj = {};
      const targetClean = selectedTargetFormat.toLowerCase();

      if (["jpg", "jpeg", "png", "webp", "bmp", "ico", "tiff"].includes(targetClean)) {
        optionsObj.quality = parseInt(qualityInput.value, 10);
        optionsObj.grayscale = grayscaleInput ? grayscaleInput.checked : false;
        if (resizeInput && resizeInput.value.trim()) {
          optionsObj.resize = resizeInput.value.trim();
        }
      }

      if (targetClean === "sql") {
        optionsObj.table_name = tableNameInput ? tableNameInput.value.trim() : "data_table";
      }

      if (["mp3", "wav"].includes(targetClean)) {
        optionsObj.lang = langInput ? langInput.value : "en";
      }

      formData.append("options", JSON.stringify(optionsObj));

      try {
        const response = await fetch("/api/convert", {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          const errJson = await response.json().catch(() => null);
          throw new Error((errJson && errJson.detail) ? errJson.detail : `Server error ${response.status}`);
        }

        // Parse filename from Content-Disposition header
        const contentDisp = response.headers.get("Content-Disposition");
        let outFilename = `converted_${currentFile.name.split('.')[0]}.${selectedTargetFormat}`;
        if (contentDisp && contentDisp.includes("filename*=UTF-8''")) {
          outFilename = decodeURIComponent(contentDisp.split("filename*=UTF-8''")[1]);
        } else if (contentDisp && contentDisp.includes("filename=")) {
          outFilename = contentDisp.split("filename=")[1].replace(/"/g, '');
        }

        const blob = await response.blob();
        if (downloadUrl) URL.revokeObjectURL(downloadUrl);
        downloadUrl = URL.createObjectURL(blob);

        // Auto download trigger
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = outFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Update result UI
        if (downloadBtn) {
          downloadBtn.href = downloadUrl;
          downloadBtn.download = outFilename;
        }
        if (resultMeta) {
          resultMeta.textContent = `${outFilename} (${formatBytes(blob.size)})`;
        }

        if (conversionPanel) conversionPanel.classList.add("hidden");
        if (resultCard) resultCard.classList.remove("hidden");

      } catch (err) {
        console.error("Conversion failed:", err);
        showError(`Conversion failed: ${err.message}`);
      } finally {
        setLoading(false);
      }
    });
  }

  // Reset File Selection
  function resetFileSelection() {
    currentFile = null;
    selectedTargetFormat = null;
    if (fileInput) fileInput.value = "";
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      downloadUrl = null;
    }
    hideError();

    if (conversionPanel) conversionPanel.classList.add("hidden");
    if (resultCard) resultCard.classList.add("hidden");
    if (dropzone) dropzone.classList.remove("hidden");
  }

  // Helpers
  function setLoading(isLoading) {
    if (!convertBtn) return;
    convertBtn.disabled = isLoading;
    if (isLoading) {
      if (convertBtnText) convertBtnText.textContent = "Processing...";
      if (spinner) spinner.classList.remove("hidden");
    } else {
      if (convertBtnText) convertBtnText.textContent = "Convert File";
      if (spinner) spinner.classList.add("hidden");
    }
  }

  function showError(msg) {
    if (errorMsg) errorMsg.textContent = msg;
    if (errorBanner) {
      errorBanner.classList.remove("hidden");
      if (typeof feather !== "undefined") feather.replace();
    }
  }

  function hideError() {
    if (errorBanner) errorBanner.classList.add("hidden");
  }

  function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
  }

  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  /* ==========================================================================
     1. Custom Interactive Cursor Engine
     ========================================================================== */
  const cursorDot = document.getElementById("cursorDot");
  const cursorRing = document.getElementById("cursorRing");

  if (cursorDot && cursorRing) {
    let mouseX = -100, mouseY = -100;
    let ringX = -100, ringY = -100;

    window.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursorDot.style.left = `${mouseX}px`;
      cursorDot.style.top = `${mouseY}px`;
    });

    function renderCursorRing() {
      ringX += (mouseX - ringX) * 0.18;
      ringY += (mouseY - ringY) * 0.18;
      cursorRing.style.left = `${ringX}px`;
      cursorRing.style.top = `${ringY}px`;
      requestAnimationFrame(renderCursorRing);
    }
    renderCursorRing();

    // Hover Scaling for Interactive Elements
    const hoverSelector = "a, button, label, input, select, .dropzone, .target-pill, .neu-btn, .neu-outset-sm";
    document.body.addEventListener("mouseover", (e) => {
      if (e.target.closest(hoverSelector)) {
        document.body.classList.add("cursor-hover");
      }
    });
    document.body.addEventListener("mouseout", (e) => {
      if (e.target.closest(hoverSelector)) {
        document.body.classList.remove("cursor-hover");
      }
    });
  }

  /* ==========================================================================
     2. Anti-Inspect & DevTools Protection Module
     ========================================================================== */
  // Disable Right-Click Context Menu
  document.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    return false;
  });

  // Block DevTools Keyboard Shortcuts
  document.addEventListener("keydown", (e) => {
    // Block F12
    if (e.keyCode === 123 || e.key === "F12") {
      e.preventDefault();
      return false;
    }
    // Block Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C (or Cmd+Option+I/J/C on Mac)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67 || e.key === "I" || e.key === "J" || e.key === "C" || e.key === "i" || e.key === "j" || e.key === "c")) {
      e.preventDefault();
      return false;
    }
    // Block Ctrl+U / Cmd+Option+U (View Source)
    if ((e.ctrlKey || e.metaKey) && (e.keyCode === 85 || e.key === "U" || e.key === "u")) {
      e.preventDefault();
      return false;
    }
  });

  // Anti-Analysis Debugger Loop Guard
  setInterval(() => {
    const startTime = performance.now();
    (function () {
      return false;
    })["constructor"]("debugger")();
    if (performance.now() - startTime > 100) {
      document.body.innerHTML = "<div style='display:flex;height:100vh;justify-content:center;align-items:center;background:#0b0c14;color:#f8fafc;font-family:sans-serif;'><h2>Security Protection Activated</h2></div>";
    }
  }, 1000);

  // Silence Console Output
  console.log = function() {};
  console.warn = function() {};
  console.debug = function() {};
  console.info = function() {};
});
