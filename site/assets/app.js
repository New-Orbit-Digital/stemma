/* Stemma site behavior: the 21+ notice and name/alias search.
   Vanilla JS, no dependencies. At runtime the site reads only data/stemma.json. */
(function () {
  "use strict";

  var AGE_KEY = "stemma_age_ok";
  var DATA_URL = "/data/stemma.json";
  var MAX_RESULTS = 20;

  /* Fold a name to comparable form: "Skunk #1" and "skunk 1" both -> "skunk1". */
  function fold(value) {
    return String(value == null ? "" : value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "");
  }

  function storage() {
    try {
      return window.localStorage;
    } catch (err) {
      return null; // private mode, or storage blocked
    }
  }

  function ageAcknowledged() {
    var store = storage();
    try {
      return !!store && store.getItem(AGE_KEY) === "1";
    } catch (err) {
      return false;
    }
  }

  function rememberAge() {
    var store = storage();
    try {
      if (store) {
        store.setItem(AGE_KEY, "1");
      }
    } catch (err) {
      /* Nothing to do: the notice just shows again next visit. */
    }
  }

  /* The notice overlays the page instead of replacing it, so the HTML stays
     readable to crawlers and nothing is redirected away. */
  function setupAgeGate() {
    var gate = document.getElementById("age-gate");
    if (!gate || ageAcknowledged()) {
      return;
    }
    var declined = document.getElementById("age-gate-declined");
    var ok = document.getElementById("age-gate-ok");
    var no = document.getElementById("age-gate-no");

    gate.hidden = false;
    gate.setAttribute("aria-hidden", "false");
    document.body.classList.add("age-gate-open");

    function dismiss() {
      rememberAge();
      gate.hidden = true;
      gate.setAttribute("aria-hidden", "true");
      document.body.classList.remove("age-gate-open");
    }

    if (ok) {
      ok.addEventListener("click", dismiss);
      ok.focus();
    }
    if (no) {
      no.addEventListener("click", function () {
        if (declined) {
          declined.hidden = false;
        }
      });
    }
  }

  function buildIndex(strains) {
    var entries = [];
    for (var i = 0; i < strains.length; i += 1) {
      var strain = strains[i];
      if (!strain || !strain.id) {
        continue;
      }
      var names = [strain.name || strain.id];
      var aliases = strain.aliases || [];
      for (var a = 0; a < aliases.length; a += 1) {
        names.push(aliases[a]);
      }
      var terms = [];
      for (var n = 0; n < names.length; n += 1) {
        var folded = fold(names[n]);
        if (folded) {
          terms.push(folded);
        }
      }
      entries.push({
        id: strain.id,
        name: strain.name || strain.id,
        aliases: aliases,
        kind: strain.kind || "",
        label: strain.traditional_label || "",
        status: strain.status || "",
        terms: terms
      });
    }
    return entries;
  }

  /* 0 exact, 1 prefix, 2 anywhere; -1 no match. */
  function score(entry, needle) {
    var best = -1;
    for (var i = 0; i < entry.terms.length; i += 1) {
      var term = entry.terms[i];
      var rank = -1;
      if (term === needle) {
        rank = 0;
      } else if (term.indexOf(needle) === 0) {
        rank = 1;
      } else if (term.indexOf(needle) > 0) {
        rank = 2;
      }
      if (rank !== -1 && (best === -1 || rank < best)) {
        best = rank;
      }
    }
    return best;
  }

  function search(entries, query) {
    var needle = fold(query);
    if (!needle) {
      return [];
    }
    var hits = [];
    for (var i = 0; i < entries.length; i += 1) {
      var rank = score(entries[i], needle);
      if (rank !== -1) {
        hits.push({ rank: rank, entry: entries[i] });
      }
    }
    hits.sort(function (a, b) {
      if (a.rank !== b.rank) {
        return a.rank - b.rank;
      }
      return a.entry.name.localeCompare(b.entry.name);
    });
    return hits.slice(0, MAX_RESULTS);
  }

  function metaLine(entry) {
    var parts = [];
    if (entry.status === "stub") {
      parts.push("not yet cataloged");
    }
    if (entry.kind) {
      parts.push(entry.kind);
    }
    if (entry.label && entry.label !== "unknown") {
      parts.push(entry.label);
    }
    if (entry.aliases && entry.aliases.length) {
      parts.push("also " + entry.aliases.join(", "));
    }
    return parts.join(" · ");
  }

  function resultItem(entry) {
    var item = document.createElement("li");
    var link = document.createElement("a");
    link.href = "/s/" + encodeURIComponent(entry.id) + "/";

    var name = document.createElement("span");
    name.className = "result__name";
    name.textContent = entry.name;
    link.appendChild(name);

    var meta = metaLine(entry);
    if (meta) {
      var small = document.createElement("span");
      small.className = "result__meta";
      small.textContent = meta;
      link.appendChild(small);
    }
    item.appendChild(link);
    return item;
  }

  function setupSearch() {
    var input = document.getElementById("search-input");
    var results = document.getElementById("search-results");
    var status = document.getElementById("search-status");
    if (!input || !results || !status) {
      return; // not the search page
    }

    var entries = null;

    function render() {
      var query = input.value;
      results.textContent = "";
      if (entries === null) {
        return;
      }
      if (!fold(query)) {
        status.textContent = entries.length
          ? "Type to search " + entries.length + " cards."
          : "The catalog is empty for now.";
        return;
      }
      var hits = search(entries, query);
      if (!hits.length) {
        status.textContent = "Not in the catalog yet.";
        return;
      }
      status.textContent = hits.length === 1 ? "1 match" : hits.length + " matches";
      for (var i = 0; i < hits.length; i += 1) {
        results.appendChild(resultItem(hits[i].entry));
      }
    }

    input.addEventListener("input", render);
    input.disabled = true;

    fetch(DATA_URL, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("HTTP " + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        entries = buildIndex((data && data.strains) || []);
        input.disabled = false;
        render();
      })
      .catch(function () {
        entries = null;
        input.disabled = false;
        status.textContent = "The catalog could not be loaded. The full list is below.";
      });
  }

  function start() {
    setupAgeGate();
    setupSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
