(() => {
  const installButton = document.getElementById("pwaInstallButton");
  let installPrompt = null;

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(error => {
        console.warn("No se pudo activar el modo instalable:", error);
      });
    });
  }

  const isInstalled = window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  if (!isInstalled && installButton) {
    window.addEventListener("beforeinstallprompt", event => {
      event.preventDefault();
      installPrompt = event;
      installButton.hidden = false;
    });

    installButton.addEventListener("click", async () => {
      if (!installPrompt) return;
      installButton.disabled = true;
      installPrompt.prompt();
      await installPrompt.userChoice;
      installPrompt = null;
      installButton.hidden = true;
      installButton.disabled = false;
    });

    window.addEventListener("appinstalled", () => {
      installPrompt = null;
      installButton.hidden = true;
    });
  }
})();
