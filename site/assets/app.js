/* Stemma site behavior: the 21+ notice, name/alias search, and the timeline's
   family filter. Vanilla JS, no dependencies. At runtime the site reads only
   data/stemma.json and the build-time JSON the pages carry inline. */
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

  /* One result row. Callers pass an href so the same list can open a card or,
     on the timeline, point at that card's family. */
  function resultItem(entry, href) {
    var item = document.createElement("li");
    var link = document.createElement("a");
    link.href = href || "/s/" + encodeURIComponent(entry.id) + "/";

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

  /* -- the timeline's family filter ------------------------------------- */

  function inlineJSON(id) {
    var node = document.getElementById(id);
    if (!node) {
      return null;
    }
    try {
      return JSON.parse(node.textContent || "null");
    } catch (err) {
      return null;
    }
  }

  function queryParam(name) {
    var pairs = String(window.location.search || "").replace(/^\?/, "").split("&");
    for (var i = 0; i < pairs.length; i += 1) {
      var pair = pairs[i].split("=");
      if (pair[0] === name) {
        return decodeURIComponent((pair[1] || "").replace(/\+/g, "%20"));
      }
    }
    return "";
  }

  /* The bars are laid out at build time, so filtering only ever hides rows:
     the axis and the decade bands never move under the filter. */
  function setupTimeline() {
    var chart = document.getElementById("timeline");
    var input = document.getElementById("family-input");
    var results = document.getElementById("family-results");
    var status = document.getElementById("family-status");
    var active = document.getElementById("timeline-active");
    if (!chart || !input || !results || !status) {
      return; // not the timeline page
    }

    var data = inlineJSON("timeline-data") || {};
    var families = data.families || {};
    var entries = buildIndex(data.strains || []);
    var names = {};
    for (var i = 0; i < entries.length; i += 1) {
      names[entries[i].id] = entries[i].name;
    }
    var rows = chart.querySelectorAll("[data-id]");
    var everything = status.textContent;
    var current = "";

    function href(id) {
      return window.location.pathname + (id ? "?family=" + encodeURIComponent(id) : "");
    }

    function apply(id) {
      var keep = null;
      if (id && families[id]) {
        keep = {};
        for (var k = 0; k < families[id].length; k += 1) {
          keep[families[id][k]] = true;
        }
      }
      var shown = 0;
      for (var r = 0; r < rows.length; r += 1) {
        var on = !keep || keep[rows[r].getAttribute("data-id")] === true;
        rows[r].classList.toggle("is-filtered", !on);
        if (on) {
          shown += 1;
        }
      }
      return { shown: shown, filtered: keep !== null };
    }

    function select(id, remember) {
      var result = apply(id);
      current = result.filtered ? id : "";
      if (result.filtered) {
        status.textContent =
          names[id] +
          " and its ancestors: " +
          result.shown +
          " of " +
          rows.length +
          " cards.";
      } else if (id) {
        status.textContent = 'No card with the id "' + id + '". Showing every card.';
      } else {
        status.textContent = everything;
      }
      if (active) {
        active.hidden = !result.filtered;
      }
      input.value = result.filtered ? names[id] : "";
      results.textContent = "";
      if (remember && window.history && window.history.pushState) {
        window.history.pushState({ family: current }, "", href(current));
      }
    }

    function render() {
      results.textContent = "";
      var hits = search(entries, input.value);
      for (var h = 0; h < hits.length; h += 1) {
        var entry = hits[h].entry;
        var row = resultItem(entry, href(entry.id));
        row.firstChild.setAttribute("data-family-id", entry.id);
        results.appendChild(row);
      }
    }

    /* Delegated, so the rows stay plain links: a middle click or "copy link"
       still gets a shareable ?family= URL. */
    function pick(event) {
      var link = event.target;
      while (link && link !== results && !link.getAttribute("data-family-id")) {
        link = link.parentNode;
      }
      var id = link && link.getAttribute && link.getAttribute("data-family-id");
      if (!id || !window.history || !window.history.pushState) {
        return;
      }
      event.preventDefault();
      select(id, true);
    }

    input.addEventListener("input", render);
    results.addEventListener("click", pick);
    if (active) {
      active.addEventListener("click", function (event) {
        var target = event.target;
        if (!target || target.id !== "timeline-clear") {
          return;
        }
        if (!window.history || !window.history.pushState) {
          return; // let the link navigate instead
        }
        event.preventDefault();
        select("", true);
      });
    }
    window.addEventListener("popstate", function () {
      select(queryParam("family"), false);
    });

    var initial = queryParam("family");
    if (initial) {
      select(initial, false);
    }
  }

  function start() {
    setupAgeGate();
    setupSearch();
    setupTimeline();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
