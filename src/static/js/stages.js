const urlParams = new URLSearchParams(window.location.search);
const goalId = urlParams.get("goal");

let stages = [];
let nodesMap = new Map();

let svg;
let canvas;

let draggingStage = null;
let offsetX = 0;
let offsetY = 0;

let connecting = false;
let connectionLine = null;
let connectionFrom = null;
let selectedStage = null;

let draggingEditor = false;
let editorOffsetX = 0;
let editorOffsetY = 0;


function initEditorDrag() {
    const editor = document.getElementById("stage-editor");

    editor.addEventListener("mousedown", (e) => {
        // чтобы не мешать вводу текста
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") {
            return;
        }

        draggingEditor = true;

        const rect = editor.getBoundingClientRect();
        editorOffsetX = e.clientX - rect.left;
        editorOffsetY = e.clientY - rect.top;

        editor.style.position = "absolute";
    });
}

// движение панели
document.addEventListener("mousemove", (e) => {
    if (!draggingEditor) return;

    const editor = document.getElementById("stage-editor");

    editor.style.left = (e.clientX - editorOffsetX) + "px";
    editor.style.top = (e.clientY - editorOffsetY) + "px";
});

// отпускание
document.addEventListener("mouseup", () => {
    draggingEditor = false;
});

// Добавление новой стадии через кнопку панели
async function createNewStage() {
    if (!canvas) return;

    // ставим по центру canvas
    const rect = canvas.getBoundingClientRect();
    const x = rect.width / 2;
    const y = rect.height / 2;

    await request(`/editor/goals/${goalId}/stages`, "POST", {
        title: "New Stage",
        latitude: y,
        longitude: x
    });

    await loadStages();
}

// 🧩 РЕНДЕР НОД с возможностью выбора
function renderNodes() {
    nodesMap.clear();
    canvas.querySelectorAll(".node").forEach(n => n.remove());

    stages.forEach(stage => {
        const div = document.createElement("div");
        div.className = "node";
        div.innerText = stage.title;

        div.style.left = (stage.longitude || 100) + "px";
        div.style.top = (stage.latitude || 100) + "px";

        // DRAG
        div.onmousedown = (e) => {
            e.preventDefault();
            if (e.shiftKey) {
                startConnection(stage, e);
                return;
            }
            draggingStage = stage;
            const rect = canvas.getBoundingClientRect();
            offsetX = e.clientX - (stage.longitude || 0);
            offsetY = e.clientY - (stage.latitude || 0);
        };

        // CLICK - выбор стадии
        div.onclick = (e) => {
            e.stopPropagation();
            selectStage(stage);
        };

        canvas.appendChild(div);
        nodesMap.set(stage.id, div);
    });
}

// Выбор стадии и открытие панели
function selectStage(stage) {
    selectedStage = stage;

    // убрать выделение у всех
    nodesMap.forEach(el => el.classList.remove("selected"));

    // выделить текущую
    const el = nodesMap.get(stage.id);
    if (el) el.classList.add("selected");

    document.getElementById("stage-title").value = stage.title;
    document.getElementById("stage-description").value = stage.description || "";
    document.getElementById("stage-status").value = stage.status;
    document.getElementById("stage-milestone").checked = stage.is_milestone;
    document.getElementById("stage-difficulty").value = stage.difficulty_level || 1;

    document.getElementById("stage-editor").classList.remove("hidden");
}

document.addEventListener("click", (e) => {
    const editor = document.getElementById("stage-editor");

    const clickedNode = e.target.closest(".node");
    const clickedEditor = e.target.closest("#stage-editor");

    // если клик НЕ по стадии и НЕ по панели
    if (!clickedNode && !clickedEditor) {
        closeStageEditor();
    }
});

function closeStageEditor() {
    selectedStage = null;

    // убрать подсветку
    nodesMap.forEach(el => el.classList.remove("selected"));

    document.getElementById("stage-editor").classList.add("hidden");
}

// Сохранение изменений стадии
async function saveStageChanges() {
    if (!selectedStage) return;

    const updated = {
        title: document.getElementById("stage-title").value,
        description: document.getElementById("stage-description").value,
        status: document.getElementById("stage-status").value,
        is_milestone: document.getElementById("stage-milestone").checked,
        difficulty_level: Number(document.getElementById("stage-difficulty").value)
    };

    await request(`/editor/goals/${goalId}/stages/${selectedStage.id}`, "PATCH", updated);
    await loadStages();
    closeStageEditor();
}

// init
async function init() {
    canvas = document.getElementById("canvas");

    svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.position = "absolute";
    svg.style.width = "100%";
    svg.style.height = "100%";

    canvas.appendChild(svg);

    initSVGMarkers();
    initEditorDrag(); // ← ВАЖНО

    await loadStages();
}

// старт
init();

// загрузка
async function loadStages() {
    stages = await request(`/editor/goals/${goalId}/stages`);
    renderNodes();
    drawConnections();
}

// 🧩 РЕНДЕР ТОЛЬКО НОД

// 🔗 ЛИНИИ (отдельно)
function drawConnections() {
    svg.innerHTML = "";

    stages.forEach(stage => {
        stage.dependency_ids.forEach(dep => {
            const from = stages.find(s => s.id === dep);
            if (!from) return;

            drawLine(from, stage);
        });
    });
}

// линия
function drawLine(from, to) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

    line.setAttribute("x1", from.longitude || 0);
    line.setAttribute("y1", from.latitude || 0);
    line.setAttribute("x2", to.longitude || 0);
    line.setAttribute("y2", to.latitude || 0);

    line.setAttribute("stroke", "#94a3b8");
    line.setAttribute("stroke-width", "2");
    line.setAttribute("marker-end", "url(#arrowhead)");

    svg.appendChild(line);
}

// Добавляем стрелку в SVG один раз при инициализации
function initSVGMarkers() {
    if (!svg) return; // ❌ если svg ещё нет, просто выходим

    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");

    marker.setAttribute("id", "arrowhead");
    marker.setAttribute("markerWidth", "10");
    marker.setAttribute("markerHeight", "7");
    marker.setAttribute("refX", "10");
    marker.setAttribute("refY", "3.5");
    marker.setAttribute("orient", "auto");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M0,0 L10,3.5 L0,7 Z");
    path.setAttribute("fill", "#94a3b8");

    marker.appendChild(path);
    defs.appendChild(marker);
    svg.appendChild(defs);
}

// в init()
initSVGMarkers();

// 🎯 ГЛОБАЛЬНЫЙ MOUSE MOVE
document.onmousemove = (e) => {

    // DRAG NODE
    if (draggingStage) {
        draggingStage.longitude = e.clientX - offsetX;
        draggingStage.latitude = e.clientY - offsetY;

        const el = nodesMap.get(draggingStage.id);
        el.style.left = draggingStage.longitude + "px";
        el.style.top = draggingStage.latitude + "px";

        drawConnections();
    }

    // DRAG CONNECTION
    if (connecting && connectionLine) {
        connectionLine.setAttribute("x2", e.clientX);
        connectionLine.setAttribute("y2", e.clientY);
    }
};

// 🛑 MOUSE UP
document.onmouseup = async (e) => {

    // сохранить координаты
    if (draggingStage) {
        await request(`/editor/goals/${goalId}/stages/${draggingStage.id}`, "PATCH", {
            latitude: draggingStage.latitude,
            longitude: draggingStage.longitude
        });

        draggingStage = null;
    }

    // завершить связь
    if (connecting) {
        finishConnection(e);
    }
};

// 🔗 НАЧАЛО СОЕДИНЕНИЯ
function startConnection(stage, e) {
    connecting = true;
    connectionFrom = stage;

    connectionLine = document.createElementNS("http://www.w3.org/2000/svg", "line");

    connectionLine.setAttribute("x1", stage.longitude);
    connectionLine.setAttribute("y1", stage.latitude);
    connectionLine.setAttribute("x2", e.clientX);
    connectionLine.setAttribute("y2", e.clientY);

    connectionLine.setAttribute("stroke", "#6366f1");
    connectionLine.setAttribute("stroke-width", "2");
    connectionLine.setAttribute("stroke-dasharray", "5,5");

    svg.appendChild(connectionLine);
}

// 🔗 КОНЕЦ СОЕДИНЕНИЯ
async function finishConnection(e) {
    connecting = false;

    if (connectionLine) {
        svg.removeChild(connectionLine);
        connectionLine = null;
    }

    const target = document.elementFromPoint(e.clientX, e.clientY);

    if (!target || !target.classList.contains("node")) return;

    const targetStage = [...nodesMap.entries()]
        .find(([id, el]) => el === target)?.[0];

    if (!targetStage || targetStage === connectionFrom.id) return;

    const stage = stages.find(s => s.id === targetStage);

    const deps = stage.dependency_ids || [];

    if (!deps.includes(connectionFrom.id)) {
        await request(`/editor/goals/${goalId}/stages/${stage.id}`, "PATCH", {
            dependency_ids: [...deps, connectionFrom.id]
        });

        await loadStages();
    }
}

// ➕ создание стадии
canvas?.addEventListener("dblclick", async (e) => {
    await request(`/editor/goals/${goalId}/stages`, "POST", {
        title: "New Stage",
        latitude: e.clientY,
        longitude: e.clientX
    });

    loadStages();
});
