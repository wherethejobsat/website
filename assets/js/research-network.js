/* Vanilla SVG research network for the Research Map page. */
(function () {
  var root = document.querySelector("[data-research-network]");
  if (!root) return;

  var svg = root.querySelector("[data-network-svg]");
  var panel = root.querySelector("[data-network-panel]");
  var filterWrap = root.querySelector("[data-network-filters]");
  var filterButtons = filterWrap ? Array.prototype.slice.call(filterWrap.querySelectorAll("[data-filter]")) : [];
  var dataUrl = root.getAttribute("data-network-src") || "/assets/data/research-network.json";
  var svgNS = "http://www.w3.org/2000/svg";
  var categoryOrder = ["All", "Working Papers", "Works in Progress", "Publications", "BLS Publications", "Zombie Papers"];
  var metadataSpecs = [
    {
      field: "topics",
      type: "topic",
      heading: "Topics",
      idPrefix: "topic",
      x: 90,
      yStart: 70,
      yStep: 92,
      labels: [
        "Employer",
        "Household",
        "workforce development",
        "remote work / telework",
        "pandemic employment",
        "vacancies",
        "workplace injuries",
        "job search",
        "Paycheck Protection Program",
        "hiring decisions",
        "Local labor markets",
        "family and household networks"
      ],
      aliases: {
        "skills gap": "workforce development",
        "firm training": "Employer",
        "business relocation": "Employer",
        "employer size": "Employer",
        "small businesses": "Employer",
        "remote work": "remote work / telework",
        "telework": "remote work / telework",
        "workplace adjustment": "remote work / telework",
        "pandemic work arrangements": "remote work / telework",
        "business closures": "pandemic employment",
        "pandemic recovery": "pandemic employment",
        "local COVID shocks": "Local labor markets",
        "industry heterogeneity": "pandemic employment",
        "local labor markets": "Local labor markets",
        "housing costs": "Local labor markets",
        "online job postings": "vacancies",
        "labor-market measurement": "vacancies",
        "heat": "workplace injuries",
        "occupational safety": "workplace injuries",
        "search behavior": "job search",
        "search frictions": "job search",
        "unemployment": "job search",
        "pandemic policy": "Paycheck Protection Program",
        "behavioral labor economics": "hiring decisions",
        "salience": "hiring decisions",
        "household finance": "Household",
        "household resources": "Household",
        "health shocks": "family and household networks",
        "family networks": "family and household networks",
        "informal insurance": "family and household networks",
        "informal family insurance": "family and household networks",
        "family decision making": "family and household networks",
        "family transfers": "family and household networks"
      }
    },
    {
      field: "data_sources",
      type: "data_source",
      heading: "Data sources",
      idPrefix: "data-source",
      x: 620,
      yStart: 70,
      yStep: 92,
      labels: [
        "QCEW",
        "CES",
        "CPS",
        "Business Response Survey",
        "PSID",
        "JOLTS",
        "SOII",
        "OEWS",
        "SBA PPP loan records",
        "online job postings"
      ],
      aliases: {
        "QCEW employment records": "QCEW",
        "QCEW employer-size frame": "QCEW",
        "QCEW wage records": "QCEW",
        "QCEW wage baseline": "QCEW",
        "QCEW sampling frame": "QCEW",
        "CES microdata": "CES",
        "CPS microdata": "CPS",
        "2018 CPS job-search supplement": "CPS",
        "BRS": "Business Response Survey",
        "2021 BRS": "Business Response Survey",
        "Vacancy Survey Data": "JOLTS",
        "vacancy survey data": "JOLTS"
      }
    }
  ];
  var state = {
    nodes: [],
    edges: [],
    nodeById: {},
    adjacency: {},
    selectedId: null,
    hoverId: null,
    filter: "All",
    canvasWidth: 1180,
    canvasHeight: 1180
  };

  function svgEl(tag, attrs) {
    var el = document.createElementNS(svgNS, tag);
    Object.keys(attrs || {}).forEach(function (key) {
      el.setAttribute(key, attrs[key]);
    });
    return el;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function typeClass(type) {
    return (type || "paper").replace(/_/g, "-");
  }

  function formatType(type) {
    if (type === "data" || type === "data_source") return "Data source";
    if (type === "topic") return "Topic";
    return "Paper";
  }

  function labelsFor(node, field) {
    if (!Array.isArray(node[field])) return [];
    return node[field].map(function (label) {
      return String(label).trim();
    }).filter(Boolean);
  }

  function mapLabel(spec, label) {
    return (spec.aliases && spec.aliases[label]) || label;
  }

  function mapLabelsFor(node, spec) {
    var allowed = new Set(spec.labels);
    var seen = new Set();
    return labelsFor(node, spec.field).map(function (label) {
      return mapLabel(spec, label);
    }).filter(function (label) {
      if (!allowed.has(label) || seen.has(label)) return false;
      seen.add(label);
      return true;
    });
  }

  function slugify(value) {
    return String(value).toLowerCase()
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function uniqueNodeId(baseId, usedIds) {
    var base = baseId || "node";
    var id = base;
    var index = 2;
    while (usedIds[id]) {
      id = base + "-" + index;
      index += 1;
    }
    usedIds[id] = true;
    return id;
  }

  function addEdge(edges, edgeKeys, sourceId, targetId) {
    var key = sourceId + "\u0000" + targetId;
    if (edgeKeys[key]) return;
    edgeKeys[key] = true;
    edges.push([sourceId, targetId]);
  }

  function expandStructuredMetadata(data) {
    var nodes = (data.nodes || []).map(function (node) {
      var copy = {};
      Object.keys(node || {}).forEach(function (key) {
        copy[key] = node[key];
      });
      return copy;
    });
    var edges = [];
    var usedIds = {};
    var edgeKeys = {};
    var generatedByKey = {};
    var maxY = 720;

    nodes.forEach(function (node) {
      if (node.id) usedIds[node.id] = true;
    });

    (data.edges || []).forEach(function (edge) {
      if (!Array.isArray(edge) || edge.length !== 2) return;
      addEdge(edges, edgeKeys, edge[0], edge[1]);
    });

    function metadataNode(spec, label) {
      var key = spec.type + "\u0000" + label;
      if (generatedByKey[key]) return generatedByKey[key];
      var node = {
        id: uniqueNodeId(spec.idPrefix + "-" + slugify(label), usedIds),
        type: spec.type,
        label: label,
        metadataField: spec.field,
        generatedMetadata: true,
        x: spec.x,
        y: spec.yStart
      };
      generatedByKey[key] = node;
      nodes.push(node);
      return node;
    }

    nodes.filter(function (node) { return node.type === "paper"; }).forEach(function (paper, index) {
      paper.x = 1010;
      paper.y = 70 + index * 62;
      maxY = Math.max(maxY, paper.y + 90);

      metadataSpecs.forEach(function (spec) {
        mapLabelsFor(paper, spec).forEach(function (label) {
          var node = metadataNode(spec, label);
          addEdge(edges, edgeKeys, paper.id, node.id);
        });
      });
    });

    metadataSpecs.forEach(function (spec) {
      var labelRank = {};
      spec.labels.forEach(function (label, index) {
        labelRank[label] = index;
      });
      var group = nodes.filter(function (node) {
        return node.generatedMetadata && node.type === spec.type;
      }).sort(function (a, b) {
        var rankA = labelRank[a.label];
        var rankB = labelRank[b.label];
        if (rankA !== undefined && rankB !== undefined && rankA !== rankB) return rankA - rankB;
        if (rankA !== undefined) return -1;
        if (rankB !== undefined) return 1;
        return a.label.localeCompare(b.label);
      });
      group.forEach(function (node, index) {
        node.x = spec.x;
        node.y = spec.yStart + index * spec.yStep;
        maxY = Math.max(maxY, node.y + 60);
      });
    });

    return {
      nodes: nodes,
      edges: edges,
      canvasWidth: 1180,
      canvasHeight: Math.max(1180, maxY)
    };
  }

  function nodeAriaLabel(node) {
    var prefix = formatType(node.type);
    var label = prefix + ": " + node.label + ".";
    if (node.type === "paper" && node.title) label += " " + node.title + ".";
    return label + " Select for details.";
  }

  function buildIndexes(data) {
    var expanded = expandStructuredMetadata(data);
    state.nodes = expanded.nodes;
    state.edges = expanded.edges;
    state.canvasWidth = expanded.canvasWidth;
    state.canvasHeight = expanded.canvasHeight;
    state.nodeById = {};
    state.adjacency = {};

    state.nodes.forEach(function (node) {
      state.nodeById[node.id] = node;
      state.adjacency[node.id] = new Set();
    });

    state.edges = state.edges.filter(function (edge) {
      var a = edge[0];
      var b = edge[1];
      if (!state.nodeById[a] || !state.nodeById[b]) return false;
      state.adjacency[a].add(b);
      state.adjacency[b].add(a);
      return true;
    });
  }

  function paperNodes() {
    return state.nodes.filter(function (node) { return node.type === "paper"; });
  }

  function neighbors(id) {
    return Array.from(state.adjacency[id] || []).map(function (neighborId) {
      return state.nodeById[neighborId];
    }).filter(Boolean);
  }

  function connectedIds(id) {
    var ids = new Set([id]);
    (state.adjacency[id] || new Set()).forEach(function (neighborId) {
      ids.add(neighborId);
    });
    return ids;
  }

  function activeNodeIds() {
    var ids = new Set();
    if (state.filter === "All") {
      state.nodes.forEach(function (node) { ids.add(node.id); });
      return ids;
    }

    paperNodes().forEach(function (paper) {
      if (paper.category !== state.filter) return;
      ids.add(paper.id);
      (state.adjacency[paper.id] || new Set()).forEach(function (neighborId) {
        ids.add(neighborId);
      });
    });
    return ids;
  }

  function firstPaperIdForFilter(filter) {
    var found = paperNodes().find(function (paper) {
      return filter === "All" || paper.category === filter;
    });
    return found ? found.id : null;
  }

  function edgeIsActive(edge, active) {
    return active.has(edge[0]) && active.has(edge[1]);
  }

  function edgeTouches(edge, id) {
    return edge[0] === id || edge[1] === id;
  }

  function edgePath(source, target) {
    var dx = target.x - source.x;
    var c1x = source.x + dx * 0.45;
    var c2x = target.x - dx * 0.45;
    return "M " + source.x + " " + source.y + " C " + c1x + " " + source.y + ", " + c2x + " " + target.y + ", " + target.x + " " + target.y;
  }

  function shapeForNode(node) {
    if (node.type === "data" || node.type === "data_source") {
      return svgEl("rect", {
        "class": "network-node-shape",
        "x": "-8",
        "y": "-8",
        "width": "16",
        "height": "16",
        "transform": "rotate(45)"
      });
    }

    return svgEl("circle", {
      "class": "network-node-shape",
      "r": node.type === "paper" ? "10.5" : "8.5"
    });
  }

  function labelAttrs(node) {
    if (node.type === "paper") {
      return { x: "0", y: "-27", anchor: "middle" };
    }
    if (node.type === "data_source") {
      return { x: "-23", y: "7", anchor: "end" };
    }
    return { x: "23", y: "7", anchor: "start" };
  }

  function renderNetwork() {
    svg.setAttribute("viewBox", "0 0 " + state.canvasWidth + " " + state.canvasHeight);
    svg.style.minWidth = "";
    svg.style.minHeight = Math.round(state.canvasHeight * 0.84) + "px";

    Array.prototype.slice.call(svg.querySelectorAll("[data-network-layer]")).forEach(function (layer) {
      layer.remove();
    });

    var edgeLayer = svgEl("g", { "class": "network-edge-layer", "data-network-layer": "edges" });
    var nodeLayer = svgEl("g", { "class": "network-node-layer", "data-network-layer": "nodes" });

    state.edges.forEach(function (edge) {
      var source = state.nodeById[edge[0]];
      var target = state.nodeById[edge[1]];
      var path = svgEl("path", {
        "class": "network-edge",
        "d": edgePath(source, target),
        "data-source": edge[0],
        "data-target": edge[1],
        "fill": "none"
      });
      edgeLayer.appendChild(path);
    });

    state.nodes.forEach(function (node) {
      var group = svgEl("g", {
        "class": "network-node network-node-" + typeClass(node.type),
        "data-node-id": node.id,
        "data-node-type": node.type,
        "transform": "translate(" + node.x + " " + node.y + ")",
        "tabindex": "0",
        "role": "button",
        "aria-label": nodeAriaLabel(node),
        "aria-pressed": "false"
      });
      var title = svgEl("title", {});
      title.textContent = node.type === "paper" && node.title ? node.title : node.label;
      group.appendChild(title);
      group.appendChild(shapeForNode(node));

      var attrs = labelAttrs(node);
      var label = svgEl("text", {
        "class": "network-node-label",
        "x": attrs.x,
        "y": attrs.y,
        "text-anchor": attrs.anchor
      });
      label.textContent = node.label;
      group.appendChild(label);

      group.addEventListener("mouseenter", function () {
        state.hoverId = node.id;
        updateState();
      });
      group.addEventListener("mouseleave", function () {
        state.hoverId = null;
        updateState();
      });
      group.addEventListener("focus", function () {
        state.hoverId = node.id;
        updateState();
      });
      group.addEventListener("blur", function () {
        state.hoverId = null;
        updateState();
      });
      group.addEventListener("click", function () {
        selectNode(node.id);
      });
      group.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectNode(node.id);
        }
      });

      nodeLayer.appendChild(group);
    });

    svg.appendChild(edgeLayer);
    svg.appendChild(nodeLayer);
  }

  function renderChips(parent, nodes) {
    var list = el("ul", "network-chip-list");
    nodes.forEach(function (node) {
      var item = el("li");
      item.appendChild(el("span", "network-chip network-chip-" + typeClass(node.type), node.label));
      list.appendChild(item);
    });
    parent.appendChild(list);
  }

  function renderLabelChips(parent, type, labels) {
    renderChips(parent, labels.map(function (label) {
      return { type: type, label: label };
    }));
  }

  function renderMetadataGroup(node, spec) {
    var labels = mapLabelsFor(node, spec);
    if (!labels.length) return;
    panel.appendChild(el("h4", null, spec.heading));
    renderLabelChips(panel, spec.type, labels);
  }

  function renderPaperPanel(node) {
    var title = el("h3", null, node.label);
    var summary = el("p", "network-panel-title", node.title);
    var meta = el("dl", "network-meta");
    [
      ["Year", node.year],
      ["Status", node.status],
      ["Category", node.category],
      ["Verification", node.needs_verification ? "Needs verification" : ""]
    ].forEach(function (pair) {
      if (!pair[1]) return;
      meta.appendChild(el("dt", null, pair[0]));
      meta.appendChild(el("dd", null, pair[1]));
    });

    panel.appendChild(el("p", "network-eyebrow", "Selected paper"));
    panel.appendChild(title);
    panel.appendChild(summary);
    panel.appendChild(meta);

    metadataSpecs.forEach(function (spec) {
      renderMetadataGroup(node, spec);
    });

    if (node.href) {
      var link = el("a", "network-detail-link", "Open on research page");
      link.href = node.href;
      panel.appendChild(link);
    }
  }

  function renderObjectPanel(node) {
    panel.appendChild(el("p", "network-eyebrow", "Selected " + formatType(node.type).toLowerCase()));
    panel.appendChild(el("h3", null, node.label));
    panel.appendChild(el("p", "network-panel-title", formatType(node.type) + " node"));

    var papers = neighbors(node.id).filter(function (item) { return item.type === "paper"; });
    if (papers.length) {
      panel.appendChild(el("h4", null, "Connected papers"));
      var list = el("ul", "network-paper-list");
      papers.forEach(function (paper) {
        var item = el("li");
        var link = el("a", null, paper.label);
        link.href = paper.href || "/research/#" + paper.id;
        item.appendChild(link);
        if (paper.category) item.appendChild(document.createTextNode(" (" + paper.category + ")"));
        if (paper.needs_verification) item.appendChild(document.createTextNode(" - needs verification"));
        list.appendChild(item);
      });
      panel.appendChild(list);
    }
  }

  function renderPanel() {
    clear(panel);
    var node = state.nodeById[state.selectedId] || state.nodeById[firstPaperIdForFilter(state.filter)];
    if (!node) {
      panel.appendChild(el("p", "network-eyebrow", "Research Network"));
      panel.appendChild(el("h3", null, "No network item selected"));
      panel.appendChild(el("p", null, "Use the fallback research links below."));
      return;
    }

    var selectedSummary = el("p", "network-selection-summary", "Selected: " + node.label);
    panel.appendChild(selectedSummary);

    if (node.type === "paper") renderPaperPanel(node);
    else renderObjectPanel(node);
  }

  function updateState() {
    var active = activeNodeIds();
    var focusId = state.hoverId || state.selectedId;
    var connected = focusId ? connectedIds(focusId) : new Set();

    Array.prototype.slice.call(svg.querySelectorAll(".network-node")).forEach(function (nodeEl) {
      var id = nodeEl.getAttribute("data-node-id");
      var isFiltered = !active.has(id);
      var isSelected = id === state.selectedId;
      var isRelated = !focusId || connected.has(id);
      nodeEl.classList.toggle("is-filtered-out", isFiltered);
      nodeEl.classList.toggle("is-selected", isSelected);
      nodeEl.classList.toggle("is-connected", !!focusId && connected.has(id) && id !== focusId);
      nodeEl.classList.toggle("is-dimmed", !!focusId && !isRelated);
      nodeEl.setAttribute("aria-pressed", isSelected ? "true" : "false");
    });

    Array.prototype.slice.call(svg.querySelectorAll(".network-edge")).forEach(function (edgeEl) {
      var edge = [edgeEl.getAttribute("data-source"), edgeEl.getAttribute("data-target")];
      var activeEdge = edgeIsActive(edge, active);
      var connectedEdge = !!focusId && edgeTouches(edge, focusId);
      edgeEl.classList.toggle("is-filtered-out", !activeEdge);
      edgeEl.classList.toggle("is-connected", connectedEdge);
      edgeEl.classList.toggle("is-dimmed", !!focusId && !connectedEdge);
    });

    filterButtons.forEach(function (button) {
      var isActive = button.getAttribute("data-filter") === state.filter;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });

    renderPanel();
  }

  function selectNode(id) {
    if (!state.nodeById[id]) return;
    state.selectedId = id;
    updateState();
  }

  function setupFilters() {
    var categoryCounts = {};
    paperNodes().forEach(function (paper) {
      categoryCounts[paper.category] = (categoryCounts[paper.category] || 0) + 1;
    });

    filterButtons.forEach(function (button) {
      var filter = button.getAttribute("data-filter");
      if (filter !== "All" && !categoryCounts[filter]) {
        button.hidden = true;
        button.disabled = true;
        return;
      }
      if (categoryOrder.indexOf(filter) === -1) return;

      button.addEventListener("click", function () {
        state.filter = filter;
        state.selectedId = firstPaperIdForFilter(filter);
        state.hoverId = null;
        updateState();
      });
    });
  }

  function showFailure() {
    root.classList.add("is-network-failed");
    clear(panel);
    panel.appendChild(el("p", "network-eyebrow", "Research Network"));
    panel.appendChild(el("h3", null, "Network data unavailable"));
    panel.appendChild(el("p", null, "The static fallback links below remain available."));
  }

  function init(data) {
    buildIndexes(data);
    setupFilters();
    renderNetwork();
    state.selectedId = firstPaperIdForFilter("All");
    updateState();
  }

  if (!window.fetch) {
    showFailure();
    return;
  }

  window.fetch(dataUrl)
    .then(function (response) {
      if (!response.ok) throw new Error("Network data request failed");
      return response.json();
    })
    .then(init)
    .catch(showFailure);
})();
