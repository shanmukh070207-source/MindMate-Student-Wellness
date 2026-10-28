// Breathing exercise, grounding exercise and journal helpers.
(function () {
  // ---------- Guided breathing: inhale 4s, hold 4s, exhale 6s ----------
  var circle = document.getElementById("breath-circle");
  if (circle) {
    var text = document.getElementById("breath-text");
    var countEl = document.getElementById("breath-count");
    var startBtn = document.getElementById("breath-start");
    var pauseBtn = document.getElementById("breath-pause");
    var resetBtn = document.getElementById("breath-reset");
    var phases = [
      { label: "Breathe in...", seconds: 4, scale: 2.2 },
      { label: "Hold...", seconds: 4, scale: 2.2 },
      { label: "Breathe out...", seconds: 6, scale: 1 }
    ];
    var phaseIndex = 0, remaining = 0, rounds = 0, timer = null;

    function showPhase() {
      var p = phases[phaseIndex];
      text.textContent = p.label + " " + remaining;
      circle.style.transitionDuration = (phaseIndex === 1 ? 0 : p.seconds) + "s";
      circle.style.transform = "scale(" + p.scale + ")";
    }

    function tick() {
      remaining -= 1;
      if (remaining <= 0) {
        phaseIndex += 1;
        if (phaseIndex >= phases.length) {
          phaseIndex = 0;
          rounds += 1;
          countEl.textContent = "Rounds completed: " + rounds;
        }
        remaining = phases[phaseIndex].seconds;
        showPhase();
      } else {
        text.textContent = phases[phaseIndex].label + " " + remaining;
      }
    }

    function start() {
      if (timer) return;
      if (remaining <= 0) { phaseIndex = 0; remaining = phases[0].seconds; }
      showPhase();
      timer = setInterval(tick, 1000);
      startBtn.disabled = true;
      pauseBtn.disabled = false;
    }
    function pause() {
      clearInterval(timer);
      timer = null;
      startBtn.textContent = "Resume";
      startBtn.disabled = false;
      pauseBtn.disabled = true;
      text.textContent = "Paused. Press Resume whenever you like.";
    }
    function reset() {
      clearInterval(timer);
      timer = null;
      phaseIndex = 0; remaining = 0; rounds = 0;
      circle.style.transitionDuration = "1s";
      circle.style.transform = "scale(1)";
      text.textContent = "Press Start when you're ready.";
      countEl.textContent = "Rounds completed: 0";
      startBtn.textContent = "Start";
      startBtn.disabled = false;
      pauseBtn.disabled = true;
    }
    startBtn.addEventListener("click", start);
    pauseBtn.addEventListener("click", pause);
    resetBtn.addEventListener("click", reset);
  }

  // ---------- Grounding: 5-4-3-2-1, one step at a time ----------
  var stepText = document.getElementById("grounding-text");
  if (stepText) {
    var steps = [
      "Look around and notice <strong>5 things you can see</strong>.",
      "Notice <strong>4 things you can feel</strong>, like your feet on the floor or the chair beneath you.",
      "Listen for <strong>3 things you can hear</strong>.",
      "Notice <strong>2 things you can smell</strong>, or recall two smells you like.",
      "Notice <strong>1 thing you can taste</strong>, or take a sip of water. Well done for taking this moment."
    ];
    var current = 0;
    var label = document.getElementById("grounding-label");
    var back = document.getElementById("grounding-back");
    var next = document.getElementById("grounding-next");
    var restart = document.getElementById("grounding-restart");

    function renderStep() {
      label.textContent = "Step " + (current + 1) + " of " + steps.length;
      stepText.innerHTML = steps[current];   // fixed text written in this file, not user input
      back.disabled = current === 0;
      next.disabled = current === steps.length - 1;
    }
    back.addEventListener("click", function () { if (current > 0) { current -= 1; renderStep(); } });
    next.addEventListener("click", function () { if (current < steps.length - 1) { current += 1; renderStep(); } });
    restart.addEventListener("click", function () { current = 0; renderStep(); });
    renderStep();
  }

  // ---------- Journal: character counter and discard ----------
  var entry = document.getElementById("entry_text");
  if (entry) {
    var counter = document.getElementById("journal-count");
    var discard = document.getElementById("journal-discard");
    var max = entry.getAttribute("maxlength");
    function updateCount() { counter.textContent = entry.value.length + " / " + max; }
    entry.addEventListener("input", updateCount);
    discard.addEventListener("click", function () {
      if (entry.value.trim() === "" || window.confirm("Discard what you've written? It has not been saved.")) {
        entry.value = "";
        updateCount();
      }
    });
    updateCount();
  }
})();
