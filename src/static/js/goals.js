async function loadGoals() {
    const goals = await request("/editor/goals");

    const container = document.getElementById("goals");
    container.innerHTML = "";

    goals.forEach(g => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <b>${g.title}</b>
            <button onclick="openStages(${g.id})">Open</button>
            <button onclick="deleteGoal(${g.id})">Delete</button>
        `;

        container.appendChild(div);
    });
}

async function createGoal() {
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;

    await request("/editor/goals", "POST", {
        title: title,
        description: description || null
    });

    loadGoals();
}

async function deleteGoal(id) {
    await request(`/editor/goals/${id}`, "DELETE");
    loadGoals();
}

function openStages(id) {
    window.location = `stages?goal=${id}`;
}

loadGoals();