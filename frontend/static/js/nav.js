(function () {
  function icon(name) {
    var map = {
      home: '<i class="bi bi-house-door-fill"></i>',
      learn: '<i class="bi bi-book-half"></i>',
      games: '<i class="bi bi-controller"></i>',
      rewards: '<i class="bi bi-trophy-fill"></i>',
      profile: '<i class="bi bi-person-fill"></i>',
      progress: '<i class="bi bi-bar-chart-line-fill"></i>',
      board: '<i class="bi bi-award-fill"></i>',
      logout: '<i class="bi bi-box-arrow-right"></i>',
    };
    return map[name] || "";
  }

  var page = document.body.getAttribute("data-page") || "";

  function item(href, key, label, match) {
    var active = match.indexOf(page) !== -1 ? " active" : "";
    return '<a class="' + active.trim() + '" href="' + href + '">' + icon(key) + "<span>" + label + "</span></a>";
  }

  var sidebar = document.getElementById("sidebar");
  if (sidebar) {
    sidebar.innerHTML =
      '<a class="logo" href="/dashboard/"><span class="logo-mark">T</span> TezMindz</a>' +
      "<nav>" +
      item("/dashboard/", "home", "Home", ["dashboard"]) +
      item("/learn/", "learn", "Learn", ["learn", "chapter", "concept", "difficulty"]) +
      item("/games/", "games", "Games", ["games", "game"]) +
      item("/progress/", "progress", "Progress", ["progress"]) +
      item("/rewards/", "rewards", "Rewards", ["rewards"]) +
      item("/leaderboard/", "board", "Leaderboard", ["leaderboard"]) +
      "</nav>" +
      '<div class="spacer"></div>' +
      '<div class="sidebar-footer">' +
        '<div class="sidebar-profile-card">' +
          '<i class="bi bi-person-circle"></i>' +
          '<div class="sidebar-profile-details">' +
            '<strong data-user-name>Student</strong>' +
            '<span>Class <span id="nav-class-num">5</span></span>' +
          '</div>' +
        '</div>' +
        '<div class="sidebar-profile-actions">' +
          '<a href="/profile/" class="btn btn-ghost btn-sm" title="Settings"><i class="bi bi-gear-fill"></i> Settings</a>' +
          '<a href="/logout/" class="btn btn-ghost btn-sm logout-btn" title="Logout"><i class="bi bi-box-arrow-right"></i></a>' +
        '</div>' +
      '</div>';
  }

  var bottom = document.getElementById("bottom-nav");
  if (bottom) {
    bottom.innerHTML =
      item("/dashboard/", "home", "Home", ["dashboard"]) +
      item("/learn/", "learn", "Learn", ["learn", "chapter", "concept", "difficulty"]) +
      item("/games/", "games", "Games", ["games", "game"]) +
      item("/rewards/", "rewards", "Rewards", ["rewards"]) +
      item("/profile/", "profile", "Profile", ["profile"]);
  }

  var nameEls = document.querySelectorAll("[data-user-name]");
  var s = window.TM && TM.get();
  if (s) {
    nameEls.forEach(function (el) {
      el.textContent = s.name;
    });
    var navClassEl = document.getElementById("nav-class-num");
    if (navClassEl) {
      navClassEl.textContent = s.classLevel;
    }
  }
})();
