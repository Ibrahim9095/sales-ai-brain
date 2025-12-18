let alerts = [
    {user: "İbrahim", type: "danger", risk: 85, last_message: "Xidmətlərinizdən narazıyam"},
    {user: "Leyla", type: "warning", risk: 65, last_message: "Qiymət çox yüksəkdir"},
  ];
  
  function renderAlerts() {
    const container = document.getElementById("alerts-container");
    const alertSound = document.getElementById("alert-sound");
    container.innerHTML = "";
    alerts.forEach(alert => {
      const card = document.createElement("div");
      card.className = `alert-card ${alert.type}`;
      card.innerHTML = `
        <h3>${alert.user} - Risk: ${alert.risk}% (${alert.type.toUpperCase()})</h3>
        <p>Son mesaj: ${alert.last_message}</p>
        <button onclick="handleIntervention('${alert.user}')">Müdaxilə et</button>
      `;
      container.appendChild(card);
  
      // Audio alert
      if(alert.type === "danger" || alert.type === "warning") {
        alertSound.play();
      }
    });
  }
  
  renderAlerts();
  