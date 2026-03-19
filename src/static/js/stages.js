const urlParams = new URLSearchParams(window.location.search);
const goalId = urlParams.get("goal");

let stages = [];

async function loadStages() {
    stages = await request(`/editor/goals/${goalId}/stages`);
    render();
}

function render() {
    const canvas = document.getElementById("canvas");
    canvas.innerHTML = "";

    // линии
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.position = "absolute";
    svg.style.width = "100%";
    svg.style.height = "100%";

    stages.forEach(stage => {
        stage.dependency_ids.forEach(dep => {
            const from = stages.find(s => s.id === dep);

            if (!from) return;

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

            line.setAttribute("x1", from.longitude);
            line.setAttribute("y1", from.latitude);
            line.setAttribute("x2", stage.longitude);
            line.setAttribute("y2", stage.latitude);

            line.setAttribute("stroke", "white");

            svg.appendChild(line);
        });
    });

    canvas.appendChild(svg);

    // ноды
    stages.forEach(stage => {
        const div = document.createElement("div");
        div.className = "node";
        div.innerText = stage.title;

        div.style.left = stage.longitude + "px";
        div.style.top = stage.latitude + "px";

        let offsetX, offsetY;

        div.onmousedown = e => {
            offsetX = e.offsetX;
            offsetY = e.offsetY;

            document.onmousemove = ev => {
                stage.longitude = ev.clientX - offsetX;
                stage.latitude = ev.clientY - offsetY;

                div.style.left = stage.longitude + "px";
                div.style.top = stage.latitude + "px";
            };

            document.onmouseup = async () => {
                document.onmousemove = null;

                await request(`/editor/goals/${goalId}/stages/${stage.id}`, "PATCH", {
                    latitude: stage.latitude,
                    longitude: stage.longitude
                });

                render();
            };
        };

        canvas.appendChild(div);
    });
}

canvas.ondblclick = async (e) => {
    await request(`/editor/goals/${goalId}/stages`, "POST", {
        title: "New Stage",
        latitude: e.clientY,
        longitude: e.clientX
    });

    loadStages();
};

loadStages();