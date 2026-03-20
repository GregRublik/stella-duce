let goals = [];
let selectedGoalId = null;

// загрузка целей
async function loadGoals() {
    goals = await request("/editor/goals");
    renderGoals();
}

// выбор цели
function selectGoal(id) {
    selectedGoalId = id;

    const goal = goals.find(g => g.id === id);

    document.getElementById("edit-title").value = goal.title;
    document.getElementById("edit-description").value = goal.description || "";
}

// создать новую цель
async function createNewGoal() {
    const newGoal = await request("/editor/goals", "POST", {
        title: "New Goal",
        description: null
    });

    await loadGoals();
    selectGoal(newGoal.id);
}

// сохранить изменения
async function saveGoal() {
    if (!selectedGoalId) return;

    const title = document.getElementById("edit-title").value;
    const description = document.getElementById("edit-description").value;

    await request(`/editor/goals/${selectedGoalId}`, "PATCH", {
        title: title,
        description: description || null
    });

    loadGoals();
}

// удалить цель
async function deleteGoal() {
    if (!selectedGoalId) return;

    const confirmed = confirm("⚠️ Вы точно хотите удалить эту цель?");
    if (!confirmed) return;

    const idToDelete = selectedGoalId;

    // 🔥 сразу убираем из массива (optimistic UI)
    goals = goals.filter(g => g.id !== idToDelete);

    selectedGoalId = null;

    document.getElementById("edit-title").value = "";
    document.getElementById("edit-description").value = "";

    renderGoals(); // 👈 сразу обновляем UI

    try {
        await request(`/editor/goals/${idToDelete}`, "DELETE");
    } catch (e) {
        // ❗ если ошибка — откатываем
        await loadGoals();
    }
}

function renderGoals() {
    const container = document.getElementById("goals-list");
    container.innerHTML = "";

    goals.forEach(g => {
        const div = document.createElement("div");
        div.className = "goal-item";
        div.innerText = g.title;

        div.onclick = () => selectGoal(g.id);

        container.appendChild(div);
    });
}

// открыть стадии
function openStages() {
    if (!selectedGoalId) return;

    window.location = `stages?goal=${selectedGoalId}`;
}

// init
loadGoals();