/* Vanilla SVG research network for the homepage. */
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
  var state = {
    nodes: [],
    edges: [],
    nodeById: {},
    adjacency: {},
    selectedId: null,
    hoverId: null,
    filter: "All"
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

  function formatType(type) {
    if (type === "data") return "Data";
    if (type === "method") return "Method";
    if (type === "topic") return "Topic";
    return "Paper";
  }

  function nodeAriaLabel(node) {
    var prefix = formatType(node.type);
    var label = prefix + ": " + node.label + ".";
    if (node.type === "paper" && node.title) label += " " + node.title + ".";
    return label + " Select for details.";
  }

  function buildIndexes(data) {
    state.nodes = (data.nodes || []).slice();
    state.edges = (data.edges || []).slice();
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
    var c1x = source.x + dx * 0.48;
    var c2x = target.x - dx * 0.48;
    return "M " + source.x + " " + source.y + " C " + c1x + " " + source.y + ", " + c2x + " " + target.y + ", " + target.x + " " + target.y;
  }

  function shapeForNode(node) {
    if (node.type === "data") {
      return svgEl("rect", {
        "class": "network-node-shape",
        "x": "-8",
        "y": "-8",
        "width": "16",
        "height": "16",
        "transform": "rotate(45)"
      });
    }

    if (node.type === "method") {
      return svgEl("rect", {
        "class": "network-node-shape",
        "x": "-9",
        "y": "-9",
        "width": "18",
        "height": "18",
        "rx": "4"
      });
    }

    return svgEl("circle", {
      "class": "network-node-shape",
      "r": node.type === "paper" ? "10.5" : "8.5"
    });
  }

  function labelAttrs(node) {
    if (node.type === "paper") {
      return { x: "0", y: "-17", anchor: "middle" };
    }
    if (node.x < 180) {
      return { x: "14", y: "4", anchor: "start" };
    }
    if (node.x > 820) {
      return { x: "-14", y: "4", anchor: "end" };
    }
    if (node.x < 500) {
      return { x: "-14", y: "4", anchor: "end" };
    }
    return { x: "14", y: "4", anchor: "start" };
  }

  function renderNetwork() {
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
        "class": "network-node network-node-" + node.type,
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
      item.appendChild(el("span", "network-chip network-chip-" + node.type, node.label));
      list.appendChild(item);
    });
    parent.appendChild(list);
  }

  function renderPaperPanel(node) {
    var title = el("h3", null, node.label);
    var summary = el("p", "network-panel-title", node.title);
    var meta = el("dl", "network-meta");
    [
      ["Year", node.year],
      ["Status", node.status],
      ["Category", node.category]
    ].forEach(function (pair) {
      if (!pair[1]) return;
      meta.appendChild(el("dt", null, pair[0]));
      meta.appendChild(el("dd", null, pair[1]));
    });

    panel.appendChild(el("p", "network-eyebrow", "Selected paper"));
    panel.appendChild(title);
    panel.appendChild(summary);
    panel.appendChild(meta);

    var linked = neighbors(node.id);
    var topics = linked.filter(function (item) { return item.type === "topic"; });
    var dataAndMethods = linked.filter(function (item) { return item.type === "data" || item.type === "method"; });

    if (topics.length) {
      panel.appendChild(el("h4", null, "Connected topics"));
      renderChips(panel, topics);
    }
    if (dataAndMethods.length) {
      panel.appendChild(el("h4", null, "Connected data and methods"));
      renderChips(panel, dataAndMethods);
    }

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
