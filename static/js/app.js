// OmniConvert Client Engine (Author: Armaan)
function initApp() {
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
  const convertBtn = document.getElementById("convertBtn");
  const progressContainer = document.getElementById("progressContainer");
  const progressBarFill = document.getElementById("progressBarFill");
  const resultCard = document.getElementById("resultCard");
  const resultMeta = document.getElementById("resultMeta");
  const downloadBtn = document.getElementById("downloadBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");

  let currentFile = null;
  let selectedTargetFormat = null;
  let downloadUrl = null;

  // Theme Management
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
      const iconName = theme === "dark" ? "sun" : "moon";
      box.innerHTML = `<i data-feather="${iconName}"></i>`;
      if (typeof feather !== "undefined") {
        feather.replace();
      }
    }
  }

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

  const dragQuoteBadge = document.getElementById("dragQuoteBadge");

  // Drag & Drop Events for Main Dropzone
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

  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", resetFileSelection);
  }

  // File Handling
  async function handleFileSelected(file) {
    currentFile = file;
    const ext = getFileExtension(file.name);
    
    if (fileName) fileName.textContent = file.name;
    if (fileMeta) fileMeta.textContent = `${formatBytes(file.size)} • .${ext.toUpperCase()}`;
    if (fileIconBadge) fileIconBadge.textContent = ext.substring(0, 4);

    if (dropzone) dropzone.style.display = "none";
    if (conversionPanel) conversionPanel.style.display = "block";
    if (resultCard) resultCard.style.display = "none";

    await loadTargetFormats(ext);
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

  function resetFileSelection() {
    currentFile = null;
    selectedTargetFormat = null;
    if (fileInput) fileInput.value = "";
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      downloadUrl = null;
    }
    if (conversionPanel) conversionPanel.style.display = "none";
    if (dropzone) dropzone.style.display = "block";
    if (resultCard) resultCard.style.display = "none";
    if (progressContainer) progressContainer.style.display = "none";
  }

  // Load Compatible Format Pills
  async function loadTargetFormats(srcExt) {
    if (!formatPills) return;
    formatPills.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">Loading available targets...</span>';
    
    try {
      const resp = await fetch(`/api/formats?src=${encodeURIComponent(srcExt)}`);
      const data = await resp.json();
      const targets = data.allowed_targets || ["pdf", "zip", "txt", "base64"];

      formatPills.innerHTML = "";
      selectedTargetFormat = targets[0];

      targets.forEach((fmt, index) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `format-pill ${index === 0 ? 'active' : ''}`;
        btn.textContent = fmt;
        btn.addEventListener("click", () => {
          formatPills.querySelectorAll(".format-pill").forEach(p => p.classList.remove("active"));
          btn.classList.add("active");
          selectedTargetFormat = fmt;
          updateOptionsVisibility(fmt);
        });
        formatPills.appendChild(btn);
      });

      updateOptionsVisibility(targets[0]);
    } catch (err) {
      console.error("Format load error:", err);
      renderFallbackTargets(srcExt);
    }
  }

  function renderFallbackTargets(srcExt) {
    if (!formatPills) return;
    const defaultTargets = ["pdf", "png", "jpg", "txt", "json", "zip"];
    formatPills.innerHTML = "";
    selectedTargetFormat = defaultTargets[0];

    defaultTargets.forEach((fmt, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `format-pill ${index === 0 ? 'active' : ''}`;
      btn.textContent = fmt;
      btn.addEventListener("click", () => {
        formatPills.querySelectorAll(".format-pill").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        selectedTargetFormat = fmt;
        updateOptionsVisibility(fmt);
      });
      formatPills.appendChild(btn);
    });
  }

  // Dynamic Options Panel Handler
  function updateOptionsVisibility(targetFmt) {
    if (!optionsGrid) return;

    const imgOptions = document.querySelectorAll(".option-group-image");
    const dataOptions = document.querySelectorAll(".option-group-data");
    const audioOptions = document.querySelectorAll(".option-group-audio");

    let hasVisibleOption = false;

    // Image options
    if (["jpg", "jpeg", "webp", "png", "bmp"].includes(targetFmt)) {
      imgOptions.forEach(opt => opt.style.display = "flex");
      hasVisibleOption = true;
    } else {
      imgOptions.forEach(opt => opt.style.display = "none");
    }

    // Data options
    if (targetFmt === "sql") {
      dataOptions.forEach(opt => opt.style.display = "flex");
      hasVisibleOption = true;
    } else {
      dataOptions.forEach(opt => opt.style.display = "none");
    }

    // Audio options
    if (targetFmt === "mp3" || targetFmt === "wav") {
      audioOptions.forEach(opt => opt.style.display = "flex");
      hasVisibleOption = true;
    } else {
      audioOptions.forEach(opt => opt.style.display = "none");
    }

    optionsGrid.style.display = hasVisibleOption ? "grid" : "none";
  }

  // Convert Trigger Button Event
  if (convertBtn) {
    convertBtn.addEventListener("click", async () => {
      if (!currentFile || !selectedTargetFormat) {
        alert("Please select a file and target format first.");
        return;
      }

      convertBtn.disabled = true;
      convertBtn.innerHTML = '<i data-feather="loader" class="spinner"></i> Converting...';
      if (typeof feather !== "undefined") feather.replace();

      if (progressContainer) progressContainer.style.display = "block";
      if (progressBarFill) progressBarFill.style.width = "30%";

      const optionsPayload = buildOptionsPayload(selectedTargetFormat);
      const formData = new FormData();
      formData.append("file", currentFile);
      formData.append("target_format", selectedTargetFormat);
      formData.append("options", JSON.stringify(optionsPayload));

      try {
        if (progressBarFill) progressBarFill.style.width = "70%";

        const response = await fetch("/api/convert", {
          method: "POST",
          body: formData
        });

        if (progressBarFill) progressBarFill.style.width = "90%";

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: "Conversion failed" }));
          throw new Error(errData.detail || "Conversion error occurred");
        }

        const blob = await response.blob();
        if (progressBarFill) progressBarFill.style.width = "100%";

        let outName = `converted_${currentFile.name.split('.')[0]}.${selectedTargetFormat}`;
        const dispHeader = response.headers.get("Content-Disposition");
        if (dispHeader && dispHeader.includes("filename=")) {
          const match = dispHeader.match(/filename="?([^"]+)"?/);
          if (match && match[1]) outName = match[1];
        }

        if (downloadUrl) URL.revokeObjectURL(downloadUrl);
        downloadUrl = URL.createObjectURL(blob);

        if (downloadBtn) {
          downloadBtn.href = downloadUrl;
          downloadBtn.download = outName;
        }
        if (resultMeta) resultMeta.textContent = `Ready! (${formatBytes(blob.size)}) - ${outName}`;
        if (resultCard) resultCard.style.display = "block";

      } catch (err) {
        alert(`Error: ${err.message}`);
      } finally {
        convertBtn.disabled = false;
        convertBtn.innerHTML = '<i data-feather="zap"></i> Convert Now';
        if (typeof feather !== "undefined") feather.replace();
        setTimeout(() => {
          if (progressContainer) progressContainer.style.display = "none";
          if (progressBarFill) progressBarFill.style.width = "0%";
        }, 1200);
      }
    });
  }

  function buildOptionsPayload(targetFmt) {
    const opts = {};
    if (["jpg", "jpeg", "webp", "png"].includes(targetFmt)) {
      const q = document.getElementById("imgQuality");
      const g = document.getElementById("imgGrayscale");
      if (q) opts.quality = parseInt(q.value, 10) || 85;
      if (g) opts.grayscale = g.value === "true";
    }
    if (targetFmt === "sql") {
      const t = document.getElementById("tableName");
      if (t) opts.table_name = t.value.trim() || "my_table";
    }
    if (["mp3", "wav"].includes(targetFmt)) {
      const l = document.getElementById("ttsLang");
      if (l) opts.lang = l.value || "en";
    }
    return opts;
  }

  // Global Drag & Drop Overlay
  initGlobalDragOverlay();
  function initGlobalDragOverlay() {
    const overlay = document.getElementById("globalDragOverlay");
    if (!overlay) return;

    let dragCounter = 0;

    window.addEventListener("dragenter", (e) => {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.types && Array.from(e.dataTransfer.types).includes("Files")) {
        dragCounter++;
        overlay.classList.add("active");
      }
    });

    window.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    window.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter <= 0) {
        dragCounter = 0;
        overlay.classList.remove("active");
      }
    });

    overlay.addEventListener("drop", (e) => {
      e.preventDefault();
      dragCounter = 0;
      overlay.classList.remove("active");

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const floatingWin = document.getElementById("floatingWindow");
        const fabBtn = document.getElementById("floatingFabBtn");

        const clickX = e.clientX;
        const clickY = e.clientY;
        let isFloatingTarget = false;

        if (floatingWin && floatingWin.classList.contains("active")) {
          const rect = floatingWin.getBoundingClientRect();
          if (clickX >= rect.left - 40 && clickX <= rect.right + 40 &&
              clickY >= rect.top - 40 && clickY <= rect.bottom + 40) {
            isFloatingTarget = true;
          }
        }

        if (fabBtn) {
          const fabRect = fabBtn.getBoundingClientRect();
          if (clickX >= fabRect.left - 40 && clickX <= fabRect.right + 40 &&
              clickY >= fabRect.top - 40 && clickY <= fabRect.bottom + 40) {
            isFloatingTarget = true;
          }
        }

        if (isFloatingTarget && typeof window.handleFloatingFileGlobal === "function") {
          window.handleFloatingFileGlobal(file);
        } else {
          handleFileSelected(file);
          const mainCard = document.querySelector(".converter-card");
          if (mainCard) mainCard.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  }

  // Draggable Floating Mini Converter Window & FAB Widget
  initFloatingWindowAndFab();
  function initFloatingWindowAndFab() {
    const fabBtn = document.getElementById("floatingFabBtn");
    const openHeaderBtn = document.getElementById("openFloatingWinBtn");
    const floatingWin = document.getElementById("floatingWindow");
    const winHeader = document.getElementById("floatingWindowHeader");
    const minimizeBtn = document.getElementById("floatingMinimizeBtn");
    const closeBtn = document.getElementById("floatingCloseBtn");

    const floatingDropzone = document.getElementById("floatingDropzone");
    const floatingFileInput = document.getElementById("floatingFileInput");
    const floatingPanel = document.getElementById("floatingPanel");
    const floatingFileName = document.getElementById("floatingFileName");
    const floatingFileMeta = document.getElementById("floatingFileMeta");
    const floatingFileBadge = document.getElementById("floatingFileBadge");
    const floatingRemoveBtn = document.getElementById("floatingRemoveFileBtn");
    const floatingFormatPills = document.getElementById("floatingFormatPills");
    const floatingConvertBtn = document.getElementById("floatingConvertBtn");
    const floatingProgressContainer = document.getElementById("floatingProgressContainer");
    const floatingProgressBarFill = document.getElementById("floatingProgressBarFill");
    const floatingResultCard = document.getElementById("floatingResultCard");
    const floatingResultMeta = document.getElementById("floatingResultMeta");
    const floatingDownloadBtn = document.getElementById("floatingDownloadBtn");

    let floatingFile = null;
    let floatingTargetFmt = null;
    let floatingDownloadUrl = null;

    // Toggle Floating Window Visibility
    window.toggleFloatingWindow = function(e) {
      if (e && e.preventDefault) {
        e.preventDefault();
        e.stopPropagation();
      }
      const win = document.getElementById("floatingWindow");
      if (!win) return;

      const isOpening = !win.classList.contains("active");

      if (isOpening) {
        win.style.top = "";
        win.style.left = "";
        win.style.right = "";
        win.style.bottom = "";
        win.style.display = "flex";

        win.classList.add("active");
        win.classList.remove("minimized");

        if (minimizeBtn) {
          minimizeBtn.innerHTML = '<i data-feather="minus" id="floatingMinimizeIcon"></i>';
          if (typeof feather !== "undefined") feather.replace();
        }

        if (currentFile && !floatingFile) {
          handleFloatingFile(currentFile);
        }
      } else {
        win.classList.remove("active");
        win.style.display = "none";
      }
    };

    const toggleFloatingWindow = window.toggleFloatingWindow;

    if (minimizeBtn && floatingWin) {
      minimizeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        floatingWin.classList.toggle("minimized");
        const isMin = floatingWin.classList.contains("minimized");
        minimizeBtn.innerHTML = isMin 
          ? '<i data-feather="maximize-2" id="floatingMinimizeIcon"></i>' 
          : '<i data-feather="minus" id="floatingMinimizeIcon"></i>';
        if (typeof feather !== "undefined") feather.replace();
      });
    }

    if (closeBtn && floatingWin) {
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        floatingWin.classList.remove("active");
        setTimeout(() => {
          if (!floatingWin.classList.contains("active")) {
            floatingWin.style.display = "none";
          }
        }, 300);
      });
    }

    // Draggable Window Physics Logic
    if (winHeader && floatingWin) {
      let isDragging = false;
      let startX, startY, initialLeft, initialTop;

      winHeader.addEventListener("mousedown", (e) => {
        if (e.target.closest(".floating-action-btn")) return;
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;

        const rect = floatingWin.getBoundingClientRect();
        initialLeft = rect.left;
        initialTop = rect.top;

        floatingWin.style.right = "auto";
        floatingWin.style.bottom = "auto";
        floatingWin.style.left = `${initialLeft}px`;
        floatingWin.style.top = `${initialTop}px`;

        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
      });

      function onMouseMove(e) {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;

        let newLeft = initialLeft + dx;
        let newTop = initialTop + dy;

        const maxLeft = window.innerWidth - floatingWin.offsetWidth - 10;
        const maxTop = window.innerHeight - floatingWin.offsetHeight - 10;

        newLeft = Math.max(10, Math.min(newLeft, maxLeft));
        newTop = Math.max(10, Math.min(newTop, maxTop));

        floatingWin.style.left = `${newLeft}px`;
        floatingWin.style.top = `${newTop}px`;
      }

      function onMouseUp() {
        isDragging = false;
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      }
    }

    // Global Expose for Floating File handling
    window.handleFloatingFileGlobal = function(file) {
      if (!floatingWin) return;
      if (!floatingWin.classList.contains("active")) {
        window.toggleFloatingWindow();
      }
      floatingWin.classList.remove("minimized");
      handleFloatingFile(file);
    };

    // Header click to expand if minimized
    if (winHeader && floatingWin) {
      winHeader.addEventListener("click", (e) => {
        if (e.target.closest(".floating-action-btn")) return;
        if (floatingWin.classList.contains("minimized")) {
          floatingWin.classList.remove("minimized");
          if (minimizeBtn) {
            minimizeBtn.innerHTML = '<i data-feather="minus" id="floatingMinimizeIcon"></i>';
            if (typeof feather !== "undefined") feather.replace();
          }
        }
      });
    }

    // Comprehensive Drag & Drop Event Handling for Floating Window, Dropzone, Panel & FAB
    const floatDropTargets = [floatingWin, floatingDropzone, floatingPanel, fabBtn];
    floatDropTargets.forEach(target => {
      if (!target) return;

      target.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (floatingWin) floatingWin.style.borderColor = "var(--accent-cyan)";
      });

      target.addEventListener("dragleave", (e) => {
        e.preventDefault();
        if (floatingWin) floatingWin.style.borderColor = "var(--accent-primary)";
      });

      target.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const overlay = document.getElementById("globalDragOverlay");
        if (overlay) overlay.classList.remove("active");

        if (floatingWin) {
          floatingWin.style.borderColor = "var(--accent-primary)";
          floatingWin.classList.remove("minimized");
          if (!floatingWin.classList.contains("active")) {
            window.toggleFloatingWindow();
          }
        }

        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleFloatingFile(e.dataTransfer.files[0]);
        }
      });
    });

    if (floatingDropzone) {
      floatingDropzone.addEventListener("click", (e) => {
        if (e.target.closest("#floatingFileInput") || e.target.closest("#floatingRemoveFileBtn") || e.target.closest(".browse-btn")) return;
        if (floatingFileInput) floatingFileInput.click();
      });
    }

    if (floatingFileInput) {
      floatingFileInput.addEventListener("click", (e) => e.stopPropagation());
      floatingFileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleFloatingFile(e.target.files[0]);
        }
      });
    }

    if (floatingRemoveBtn) {
      floatingRemoveBtn.addEventListener("click", () => {
        floatingFile = null;
        floatingTargetFmt = null;
        if (floatingFileInput) floatingFileInput.value = "";
        if (floatingDownloadUrl) {
          URL.revokeObjectURL(floatingDownloadUrl);
          floatingDownloadUrl = null;
        }
        if (floatingPanel) floatingPanel.style.display = "none";
        if (floatingDropzone) floatingDropzone.style.display = "block";
        if (floatingResultCard) floatingResultCard.style.display = "none";
      });
    }

    async function handleFloatingFile(file) {
      floatingFile = file;
      const ext = getFileExtension(file.name);

      if (floatingFileName) floatingFileName.textContent = file.name;
      if (floatingFileMeta) floatingFileMeta.textContent = `${formatBytes(file.size)} • .${ext.toUpperCase()}`;
      if (floatingFileBadge) floatingFileBadge.textContent = ext.substring(0, 4);

      if (floatingDropzone) floatingDropzone.style.display = "none";
      if (floatingPanel) floatingPanel.style.display = "block";
      if (floatingResultCard) floatingResultCard.style.display = "none";

      await loadFloatingTargets(ext);
    }

    async function loadFloatingTargets(srcExt) {
      if (!floatingFormatPills) return;
      floatingFormatPills.innerHTML = '<span style="color: var(--text-muted); font-size: 0.75rem;">Loading...</span>';
      try {
        const resp = await fetch(`/api/formats?src=${encodeURIComponent(srcExt)}`);
        const data = await resp.json();
        const targets = data.allowed_targets || ["pdf", "png", "txt", "zip"];

        floatingFormatPills.innerHTML = "";
        floatingTargetFmt = targets[0];

        targets.forEach((fmt, idx) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = `format-pill ${idx === 0 ? 'active' : ''}`;
          btn.textContent = fmt;
          btn.addEventListener("click", () => {
            floatingFormatPills.querySelectorAll(".format-pill").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            floatingTargetFmt = fmt;
          });
          floatingFormatPills.appendChild(btn);
        });
      } catch (err) {
        console.error("Floating format error:", err);
      }
    }

    // Floating Convert Execution
    if (floatingConvertBtn) {
      floatingConvertBtn.addEventListener("click", async () => {
        if (!floatingFile || !floatingTargetFmt) {
          alert("Please select a file for conversion in the floating window.");
          return;
        }

        floatingConvertBtn.disabled = true;
        floatingConvertBtn.innerHTML = '<i data-feather="loader" class="spinner"></i> Converting...';
        if (typeof feather !== "undefined") feather.replace();

        if (floatingProgressContainer) floatingProgressContainer.style.display = "block";
        if (floatingProgressBarFill) floatingProgressBarFill.style.width = "40%";

        const optionsPayload = buildOptionsPayload(floatingTargetFmt);
        const formData = new FormData();
        formData.append("file", floatingFile);
        formData.append("target_format", floatingTargetFmt);
        formData.append("options", JSON.stringify(optionsPayload));

        try {
          if (floatingProgressBarFill) floatingProgressBarFill.style.width = "75%";

          const response = await fetch("/api/convert", {
            method: "POST",
            body: formData
          });

          if (floatingProgressBarFill) floatingProgressBarFill.style.width = "95%";

          if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: "Conversion failed" }));
            throw new Error(errData.detail || "Conversion error occurred");
          }

          const blob = await response.blob();
          if (floatingProgressBarFill) floatingProgressBarFill.style.width = "100%";

          let outName = `converted_${floatingFile.name.split('.')[0]}.${floatingTargetFmt}`;
          const dispHeader = response.headers.get("Content-Disposition");
          if (dispHeader && dispHeader.includes("filename=")) {
            const match = dispHeader.match(/filename="?([^"]+)"?/);
            if (match && match[1]) outName = match[1];
          }

          if (floatingDownloadUrl) URL.revokeObjectURL(floatingDownloadUrl);
          floatingDownloadUrl = URL.createObjectURL(blob);

          if (floatingDownloadBtn) {
            floatingDownloadBtn.href = floatingDownloadUrl;
            floatingDownloadBtn.download = outName;
          }
          if (floatingResultMeta) floatingResultMeta.textContent = `Ready! (${formatBytes(blob.size)}) - ${outName}`;
          if (floatingResultCard) floatingResultCard.style.display = "block";

        } catch (err) {
          alert(`Floating Error: ${err.message}`);
        } finally {
          floatingConvertBtn.disabled = false;
          floatingConvertBtn.innerHTML = '<i data-feather="zap"></i> Convert Now';
          if (typeof feather !== "undefined") feather.replace();
          setTimeout(() => {
            if (floatingProgressContainer) floatingProgressContainer.style.display = "none";
            if (floatingProgressBarFill) floatingProgressBarFill.style.width = "0%";
          }, 1000);
        }
      });
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
