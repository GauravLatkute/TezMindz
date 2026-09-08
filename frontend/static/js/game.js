(function () {
  var plate = document.getElementById("plate");
  var tray = document.getElementById("tray");
  var submit = document.getElementById("submit");
  var hintBtn = document.getElementById("hint-btn");
  var explainBtn = document.getElementById("explain-btn");
  var feedback = document.getElementById("feedback");
  var hintText = document.getElementById("hint-text");
  var dots = document.querySelectorAll(".hint-dot");
  var countLabel = document.getElementById("on-plate");
  var hintCountLabel = document.getElementById("hint-count");

  // Read config injected from the Django template
  var config = window.GAME_CONFIG || { gameId: 1, difficulty: "medium", csrfToken: "" };

  var sessionId = null;
  var questionId = null;
  var questionOptions = [];
  var hintsUsed = 0;
  var solved = false;
  var startTime = Date.now();

  function onPlate() {
    return plate.querySelectorAll(".slice").length;
  }

  function updateCount() {
    countLabel.textContent = onPlate() + " / 4 slices on the plate";
  }

  function moveSlice(slice, target) {
    target.appendChild(slice);
    updateCount();
  }

  // Initialize event listeners on visual slices
  tray.querySelectorAll(".slice").forEach(function (slice) {
    slice.addEventListener("click", function () {
      if (solved) return;
      moveSlice(slice, plate);
    });
  });

  plate.addEventListener("click", function (e) {
    var slice = e.target.closest(".slice");
    if (!slice || solved) return;
    moveSlice(slice, tray);
  });

  function showFeedback(kind, html) {
    feedback.className = "card feedback " + kind + " pop";
    feedback.innerHTML = html;
    feedback.classList.remove("hidden");
  }

  // 1. Fetch game details and start session from backend
  fetch("/api/games/" + config.gameId + "/start/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": config.csrfToken
    },
    body: JSON.stringify({ difficulty: config.difficulty })
  })
  .then(function(res) {
    if (res.ok) return res.json();
    throw new Error("Failed to initialize game session");
  })
  .then(function(resData) {
    if (resData.success) {
      sessionId = resData.data.session_id;
      var questions = resData.data.questions;
      if (questions && questions.length > 0) {
        // We assume the first question is the visual pizza question
        var question = questions[0];
        questionId = question.id;
        questionOptions = question.options;
        document.querySelector("h1").textContent = question.text;
      }
    }
  })
  .catch(function(err) {
    console.error(err);
    // Local fallback if backend seeding has issues
    sessionId = 1;
    questionId = 1;
    questionOptions = [
      { id: 1, text: "1/4" },
      { id: 2, text: "2/4" },
      { id: 3, text: "3/4" },
      { id: 4, text: "4/4" }
    ];
  });

  // 2. Submit answer to backend
  submit.addEventListener("click", function () {
    if (solved || !sessionId || !questionId) return;

    var n = onPlate();
    var selectedText = n + "/4";
    var selectedOption = questionOptions.find(function(opt) {
      return opt.text === selectedText;
    });

    if (!selectedOption) {
      // Fallback to sending the first option if none matches visual state representation
      selectedOption = questionOptions[0] || { id: 1 };
    }

    var timeTaken = Math.round((Date.now() - startTime) / 1000);

    fetch("/api/games/" + sessionId + "/submit/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": config.csrfToken
      },
      body: JSON.stringify({
        question_id: questionId,
        selected_option_id: selectedOption.id,
        time_taken: timeTaken,
        hints_used: hintsUsed
      })
    })
    .then(function(res) {
      if (res.ok) return res.json();
      throw new Error("Failed to evaluate answer");
    })
    .then(function(resData) {
      if (resData.success) {
        var isCorrect = resData.data.is_correct;
        var explanation = resData.data.explanation;
        
        if (isCorrect) {
          solved = true;
          // Build feedback HTML
          var correctHtml = "<h2>Awesome!</h2><p>" + explanation + "</p>" +
            '<div class="reward-pills"><span class="pill">+' + resData.data.points_earned + ' XP</span></div>' +
            '<button id="finish-btn" class="btn btn-primary btn-block" style="margin-top: 10px;">See results</button>';
          
          showFeedback("ok", correctHtml);
          
          // Add listener to the dynamically created See Results button
          document.getElementById("finish-btn").addEventListener("click", function() {
            completeSession();
          });
        } else {
          feedback.classList.add("shake");
          setTimeout(function () {
            feedback.classList.remove("shake");
          }, 400);

          var picked = n === 0 ? "nothing" : n + "/4";
          showFeedback(
            "almost",
            "<h2>Almost there!</h2><p>You placed <strong>" + picked + "</strong> on the plate.</p>" +
            "<p class='muted small'>" + explanation + "</p>"
          );
        }
      }
    })
    .catch(function(err) {
      console.error(err);
      // Client-side fallback if backend fails
      if (n === 3) {
        solved = true;
        showFeedback(
          "ok",
          "<h2>Awesome!</h2><p>That’s exactly right. 3 out of 4 equal slices is 3/4.</p>" +
          '<div class="reward-pills"><span class="pill">+20 XP</span><span class="pill">+10 coins</span></div>' +
          '<a class="btn btn-primary btn-block" href="/result/">See results</a>'
        );
      } else {
        feedback.classList.add("shake");
        setTimeout(function () {
          feedback.classList.remove("shake");
        }, 400);
        showFeedback("almost", "<h2>Almost there!</h2><p>Check your slice count and try again.</p>");
      }
    });
  });

  // 3. Request hint from backend
  hintBtn.addEventListener("click", function () {
    if (solved || !sessionId || !questionId) return;

    if (hintsUsed >= 3) {
      hintText.textContent = "You’ve used all 3 hints. Review the explanation and try again.";
      hintText.classList.remove("hidden");
      return;
    }

    fetch("/api/questions/" + questionId + "/hint/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": config.csrfToken
      },
      body: JSON.stringify({ session_id: sessionId })
    })
    .then(function(res) {
      if (res.ok) return res.json();
      return res.json().then(function(err) { throw err; });
    })
    .then(function(resData) {
      if (resData.success) {
        hintText.textContent = resData.data.text;
        if (dots[hintsUsed]) {
          dots[hintsUsed].classList.add("used");
        }
        hintsUsed += 1;
        hintText.classList.remove("hidden");
        hintCountLabel.textContent = hintsUsed + " / 3";
      }
    })
    .catch(function(err) {
      console.error(err);
      var fallbackHints = [
        "Think about the total number of equal parts in the whole pizza.",
        "3/4 means three slices are taken — not two.",
        "Move slices until the plate shows 3 pieces. That’s 3 out of 4."
      ];
      hintText.textContent = fallbackHints[hintsUsed] || "Try reviewing the concept lesson.";
      if (dots[hintsUsed]) {
        dots[hintsUsed].classList.add("used");
      }
      hintsUsed += 1;
      hintText.classList.remove("hidden");
      hintCountLabel.textContent = hintsUsed + " / 3";
    });
  });

  // 4. Request AI Tutor Explanation for wrong answers
  explainBtn.addEventListener("click", function () {
    if (!sessionId || !questionId) return;
    
    var n = onPlate();
    var selectedText = n + "/4";
    var selectedOption = questionOptions.find(function(opt) {
      return opt.text === selectedText;
    });
    
    if (!selectedOption) {
      selectedOption = questionOptions[0] || { id: 1 };
    }

    fetch("/api/ai/feedback/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": config.csrfToken
      },
      body: JSON.stringify({
        question_id: questionId,
        selected_option_id: selectedOption.id
      })
    })
    .then(function(res) {
      if (res.ok) return res.json();
      throw new Error("AI feedback unavailable");
    })
    .then(function(resData) {
      if (resData.success) {
        var feedbackMsg = resData.data.feedback;
        showFeedback(
          "almost", 
          "<div class='tezbuddy' style='padding:0'><div class='buddy-face'>🤖</div><div><strong>TezBuddy</strong><p>" + feedbackMsg + "</p></div></div>"
        );
      }
    })
    .catch(function(err) {
      console.error(err);
      var cls = (window.USER_DATA && window.USER_DATA.classLevel) || 5;
      var msg = cls <= 5
        ? "You chose " + n + " slice(s). The bottom number of 3/4 is 4 — that’s how many equal pieces. The top number is 3 — how many you take. Put 3 slices on the plate."
        : "3/4 is three equal parts of a whole divided into four. Your plate currently shows " + n + " parts. Adjust until the numerator is 3.";
      showFeedback("almost", "<div class='tezbuddy' style='padding:0'><div class='buddy-face'>🤖</div><div><strong>TezBuddy</strong><p>" + msg + "</p></div></div>");
    });
  });

  // 5. Complete session
  function completeSession() {
    fetch("/api/games/" + sessionId + "/complete/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": config.csrfToken
      }
    })
    .then(function(res) {
      if (res.ok) return res.json();
      throw new Error("Failed to finalize session");
    })
    .then(function(resData) {
      if (resData.success) {
        location.href = "/result/";
      }
    })
    .catch(function(err) {
      console.error(err);
      location.href = "/result/";
    });
  }

  updateCount();
})();
