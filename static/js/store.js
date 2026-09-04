(function (global) {
  var KEY = "tezmindz_proto_v1";

  var defaults = {
    name: "Aarav",
    age: 11,
    email: "aarav@tezmindz.in",
    classLevel: 5,
    xp: 720,
    xpNext: 1000,
    level: 8,
    coins: 450,
    streak: 7,
    badges: 12,
    fractionsProgress: 80,
    mathProgress: 72,
    scienceProgress: 61,
    englishProgress: 80,
    hintsUsed: 0,
    lastGame: null,
    loggedIn: false,
  };

  function load() {
    if (window.USER_DATA) {
      return Object.assign({}, defaults, window.USER_DATA);
    }
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return Object.assign({}, defaults);
      return Object.assign({}, defaults, JSON.parse(raw));
    } catch (e) {
      return Object.assign({}, defaults);
    }
  }

  function save(state) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  var state = load();

  global.TM = {
    get: function () {
      return state;
    },
    set: function (patch) {
      Object.assign(state, patch);
      save(state);
      return state;
    },
    loginDemo: function (extra) {
      state = Object.assign({}, defaults, extra || {}, { loggedIn: true });
      save(state);
      return state;
    },
    requireAuth: function () {
      if (!state.loggedIn) {
        window.location.href = "/login/";
      }
    },
    greeting: function () {
      var h = new Date().getHours();
      if (h < 12) return "Good morning";
      if (h < 17) return "Good afternoon";
      return "Good evening";
    },
  };
})(window);
