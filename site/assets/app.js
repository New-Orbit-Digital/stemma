/* Stemma site behavior: the 21+ notice, name/alias search, the timeline's
   family filter, and the origin map. Vanilla JS; the map page is the one page
   with a library, Leaflet, pinned in its own <head>. At runtime the site reads
   only data/stemma.json and the build-time JSON the pages carry inline. */
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

  /* -- the origin map --------------------------------------------------- */

  var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  var TILE_ATTRIBUTION =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  var WORLD_VIEW = [20, 0];
  var WORLD_ZOOM = 2;
  var FIT_MAX_ZOOM = 5;

  function markerRadius(count) {
    return count > 1 ? Math.min(8 + 3 * (count - 1), 18) : 8;
  }

  /* Built as DOM rather than markup, so a name with an ampersand or a bracket
     in it is text and never parsed. */
  function markerPopup(place, members) {
    var wrap = document.createElement("div");
    wrap.className = "map-popup";
    if (place) {
      var title = document.createElement("p");
      title.className = "map-popup__place";
      title.textContent = place;
      wrap.appendChild(title);
    }
    var list = document.createElement("ul");
    list.className = "map-popup__list";
    for (var i = 0; i < members.length; i += 1) {
      list.appendChild(resultItem({ id: members[i].id, name: members[i].name }));
    }
    wrap.appendChild(list);
    return wrap;
  }

  function plural(count, word) {
    return count + " " + word + (count === 1 ? "" : "s");
  }

  function setupMap() {
    var container = document.getElementById("map");
    var input = document.getElementById("map-family-input");
    var results = document.getElementById("map-results");
    var status = document.getElementById("map-status");
    var active = document.getElementById("map-active");
    if (!container || !input || !results || !status) {
      return; // not the map page
    }

    var data = inlineJSON("map-data") || {};
    var groups = data.groups || [];
    var arcs = data.arcs || [];
    var families = data.families || {};
    var unknownIds = data.unknown || [];
    var entries = buildIndex(data.strains || []);
    var names = {};
    for (var i = 0; i < entries.length; i += 1) {
      names[entries[i].id] = entries[i].name;
    }
    var placeRows = document.querySelectorAll(".map-place");
    var rows = document.querySelectorAll(
      ".map-places [data-id], .map-unknown [data-id]"
    );
    var unknownBlock = document.querySelector(".map-unknown");
    var everything = status.textContent;
    var current = "";
    var placedTotal = 0;
    for (var g = 0; g < groups.length; g += 1) {
      placedTotal += (groups[g].members || []).length;
    }

    var map = null;
    var markerLayer = null;
    var arcLayer = null;
    if (window.L && groups.length) {
      /* The wheel would otherwise swallow the page scroll on the way past the
         map; the zoom controls and pinch still work. */
      map = window.L.map(container, { scrollWheelZoom: false });
      window.L.tileLayer(TILE_URL, {
        attribution: TILE_ATTRIBUTION,
        maxZoom: 18
      }).addTo(map);
      markerLayer = window.L.layerGroup().addTo(map);
      arcLayer = window.L.layerGroup().addTo(map);
      map.setView(WORLD_VIEW, WORLD_ZOOM);
    } else {
      container.className = "map map--unavailable";
      container.textContent = groups.length
        ? "The map could not be loaded. Every origin is listed below."
        : "No card has an origin we can place yet.";
    }

    /* The family is the ancestor walk the build shipped; filtering is only ever
       an intersection with it, here and in tools/origins.py alike. */
    function keepSet(id) {
      if (!id || !families[id]) {
        return null;
      }
      var keep = {};
      for (var k = 0; k < families[id].length; k += 1) {
        keep[families[id][k]] = true;
      }
      return keep;
    }

    function shown(keep) {
      var out = { placed: 0, places: 0, arcs: 0, unknown: 0 };
      for (var n = 0; n < groups.length; n += 1) {
        var members = groups[n].members || [];
        var kept = 0;
        for (var m = 0; m < members.length; m += 1) {
          if (!keep || keep[members[m].id] === true) {
            kept += 1;
          }
        }
        if (kept) {
          out.places += 1;
          out.placed += kept;
        }
      }
      for (var a = 0; a < arcs.length; a += 1) {
        if (!keep || (keep[arcs[a].child] === true && keep[arcs[a].parent] === true)) {
          out.arcs += 1;
        }
      }
      for (var u = 0; u < unknownIds.length; u += 1) {
        if (!keep || keep[unknownIds[u]] === true) {
          out.unknown += 1;
        }
      }
      return out;
    }

    function draw(keep) {
      if (!map) {
        return;
      }
      markerLayer.clearLayers();
      arcLayer.clearLayers();
      var bounds = [];
      for (var n = 0; n < groups.length; n += 1) {
        var group = groups[n];
        var members = [];
        for (var m = 0; m < (group.members || []).length; m += 1) {
          if (!keep || keep[group.members[m].id] === true) {
            members.push(group.members[m]);
          }
        }
        if (!members.length) {
          continue;
        }
        bounds.push([group.lat, group.lon]);
        window.L.circleMarker([group.lat, group.lon], {
          className: "map-marker",
          radius: markerRadius(members.length),
          weight: 2
        })
          .bindPopup(markerPopup(group.place, members))
          .bindTooltip(
            group.place
              ? group.place + " — " + plural(members.length, "strain")
              : plural(members.length, "strain")
          )
          .addTo(markerLayer);
      }
      for (var a = 0; a < arcs.length; a += 1) {
        var arc = arcs[a];
        if (keep && !(keep[arc.child] === true && keep[arc.parent] === true)) {
          continue;
        }
        /* One style for every arc: the lines on the map say the same thing
           the lines in a lineage graph do, and nothing more. */
        window.L.polyline(arc.points, { className: "map-arc", weight: 2.5 })
          .bindTooltip(
            (names[arc.parent] || arc.parent) + " → " + (names[arc.child] || arc.child)
          )
          .addTo(arcLayer);
      }
      if (bounds.length) {
        map.fitBounds(bounds, { padding: [34, 34], maxZoom: FIT_MAX_ZOOM });
      } else {
        map.setView(WORLD_VIEW, WORLD_ZOOM);
      }
    }

    /* The lists under the map are the map in text, so they filter with it. */
    function applyRows(keep) {
      for (var r = 0; r < rows.length; r += 1) {
        var on = !keep || keep[rows[r].getAttribute("data-id")] === true;
        rows[r].classList.toggle("is-filtered", !on);
      }
      for (var p = 0; p < placeRows.length; p += 1) {
        var kept = placeRows[p].querySelectorAll("[data-id]:not(.is-filtered)");
        placeRows[p].classList.toggle("is-filtered", kept.length === 0);
      }
      if (unknownBlock) {
        var left = unknownBlock.querySelectorAll("[data-id]:not(.is-filtered)");
        unknownBlock.classList.toggle(
          "is-filtered",
          keep !== null && left.length === 0
        );
      }
    }

    function href(id) {
      return window.location.pathname + (id ? "?family=" + encodeURIComponent(id) : "");
    }

    function select(id, remember) {
      var keep = keepSet(id);
      var counts = shown(keep);
      draw(keep);
      applyRows(keep);
      current = keep ? id : "";
      if (keep) {
        var text =
          names[id] +
          " and its ancestors: " +
          counts.placed +
          " of " +
          placedTotal +
          " cards on the map, " +
          plural(counts.arcs, "line") +
          ".";
        if (counts.unknown) {
          text += " " + counts.unknown + " with an unknown origin.";
        }
        status.textContent = text;
      } else if (id) {
        status.textContent = 'No card with the id "' + id + '". Showing every card.';
      } else {
        status.textContent = everything;
      }
      if (active) {
        active.hidden = !keep;
      }
      input.value = keep ? names[id] : "";
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
        if (!target || target.id !== "map-clear") {
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
    } else {
      draw(null);
    }
  }

  function start() {
    setupAgeGate();
    setupSearch();
    setupTimeline();
    setupMap();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
