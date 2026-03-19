const API_URL = "http://localhost:8000";

function getToken() {
    return localStorage.getItem("access");
}

async function request(url, method = "GET", data = null) {
    const res = await fetch(API_URL + url, {
        method,
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getToken()
        },
        body: data ? JSON.stringify(data) : null
    });

    const json = await res.json();

    if (!json.success) {
        alert(json.error);
        throw new Error(json.error);
    }

    return json.data;
}