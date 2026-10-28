// Chat page: sends the message to the server and shows the reply.
// Nothing is stored in the browser either.
(function () {
  var form = document.getElementById("chat-form");
  var input = document.getElementById("chat-input");
  var log = document.getElementById("chat-log");
  var status = document.getElementById("chat-status");
  var sendBtn = document.getElementById("chat-send");
  if (!form) return;

  function addMessage(kind, text, extra) {
    var wrap = document.createElement("div");
    wrap.className = "msg msg-" + kind + ((extra && extra.cls) ? " " + extra.cls : "");
    var who = document.createElement("span");
    who.className = "msg-who";
    who.textContent = kind === "user" ? "You" : "MindMate";
    var p = document.createElement("p");
    p.textContent = text;           // textContent keeps user text from being treated as HTML
    wrap.appendChild(who);
    wrap.appendChild(p);
    log.appendChild(wrap);
    log.scrollTop = log.scrollHeight;
    return wrap;
  }

  function addBotReply(data) {
    var el = addMessage("bot", data.message, { cls: data.safety ? "msg-safety" : "" });

    if (data.contacts && data.contacts.length) {
      var ul = document.createElement("ul");
      ul.className = "plain-list";
      data.contacts.forEach(function (c) {
        var li = document.createElement("li");
        li.textContent = c.name + ": " + c.detail;
        ul.appendChild(li);
      });
      el.appendChild(ul);
    }

    if (data.actions && data.actions.length) {
      var row = document.createElement("div");
      row.className = "msg-actions";
      data.actions.forEach(function (a) {
        var link = document.createElement("a");
        link.className = "btn btn-small btn-secondary";
        link.href = a.url;
        link.textContent = a.label;
        row.appendChild(link);
      });
      el.appendChild(row);
    }

    var note = document.createElement("p");
    note.className = "msg-note";
    if (data.safety) {
      var more = document.createElement("a");
      more.href = "/safety";
      more.textContent = "More safety information";
      note.appendChild(more);
    } else {
      note.textContent = "This is only an approximate reading of your message, not an assessment.";
    }
    el.appendChild(note);
    log.scrollTop = log.scrollHeight;
  }

  function send() {
    var text = input.value.trim();
    if (!text) {
      status.textContent = "Please type a message before sending.";
      input.focus();
      return;
    }
    status.textContent = "";
    addMessage("user", text);
    input.value = "";
    sendBtn.disabled = true;
    var typing = addMessage("bot", "Thinking...", { cls: "typing" });

    fetch(window.MINDMATE.chatUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": window.MINDMATE.csrf },
      body: JSON.stringify({ message: text })
    })
      .then(function (res) {
        return res.json().then(function (data) { return { ok: res.ok, data: data }; });
      })
      .then(function (result) {
        log.removeChild(typing);
        if (result.ok) {
          addBotReply(result.data);
        } else {
          addMessage("bot", result.data.error || "Sorry, something went wrong.", { cls: "msg-error" });
        }
      })
      .catch(function () {
        log.removeChild(typing);
        addMessage("bot", "I couldn't reach the server. Please check that MindMate is still running and try again.", { cls: "msg-error" });
      })
      .finally(function () {
        sendBtn.disabled = false;
        input.focus();
      });
  }

  form.addEventListener("submit", function (e) { e.preventDefault(); send(); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });
})();
