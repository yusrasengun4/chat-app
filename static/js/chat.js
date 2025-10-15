
// === Socket.IO bağlantısı ===
const socket = io();

// === Kullanıcı oturumu ===
let currentUser = null;
let currentChat = { type: null, id: null, name: null };

// === HTML elemanları ===
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const messagesDiv = document.getElementById("messages");
const sendBtn = document.getElementById("send-btn");
const chatTitle = document.getElementById("chat-title");
const chatSubtitle = document.getElementById("chat-subtitle");
const usersList = document.getElementById("users-list");
const groupsList = document.getElementById("groups-list");
const broadcastBtn = document.getElementById("broadcast-btn");

// === 1️⃣ Oturum kontrolü ===
async function checkSession() {
    const res = await fetch("/auth/check-session");
    const data = await res.json();

    if (!data.logged_in) {
        alert("Oturum bulunamadı. Lütfen giriş yapın.");
        window.location.href = "/auth/login";
    } else {
        currentUser = data.user;
        console.log("✅ Giriş yapan:", currentUser);
        socket.emit("join", currentUser.username);
        loadUsers();
        loadGroups();
    }
}

// === 2️⃣ Kullanıcı listesini yükle ===
async function loadUsers() {
    const res = await fetch("/api/users");
    const data = await res.json();
    usersList.innerHTML = "";

    data.forEach(user => {
        if (user.username !== currentUser.username) {
            const div = document.createElement("div");
            div.className = "p-2 border rounded-lg cursor-pointer hover:bg-blue-100";
            div.textContent = user.username;
            div.onclick = () => selectChat("private", user.id, user.username);
            usersList.appendChild(div);
        }
    });
}

// === 3️⃣ Grup listesini yükle ===
async function loadGroups() {
    const res = await fetch("/api/groups/all");
    const data = await res.json();
    groupsList.innerHTML = "";

    if (data.success && data.groups.length > 0) {
        data.groups.forEach(group => {
            const div = document.createElement("div");
            div.className = "p-2 border rounded-lg cursor-pointer hover:bg-green-100";
            div.textContent = group.group_name;
            div.onclick = () => selectChat("group", group.id, group.group_name);
            groupsList.appendChild(div);
        });
    } else {
        groupsList.innerHTML = "<p class='text-gray-500'>Henüz grup yok</p>";
    }
}

// === 4️⃣ Sohbet seçimi ===
async function selectChat(type, id, name) {
    currentChat = { type, id, name };
    chatTitle.textContent = type === "group" ? `${name} Grubu` : `${name} ile Sohbet`;
    chatSubtitle.textContent = type === "group" ? "Grup sohbeti" : "Özel mesaj";
    messageInput.disabled = false;
    sendBtn.disabled = false;
    messagesDiv.innerHTML = "";

    socket.emit("join_room", { room_type: type, room_id: id });

    // 🔹 Grup geçmiş mesajları yükle
    if (type === "group") {
        try {
            const res = await fetch(`/api/messages/group/${id}?limit=100`, {
                method: "GET",
                credentials: "include"
            });
            const data = await res.json();
            console.log("📜 Mesaj geçmişi:", data);

            if (data.success) {
                data.messages.forEach(msg => {
                    addMessageToUI({
                        sender: msg.sender_name,
                        content: msg.message_content
                    }, msg.sender_name === currentUser.username);
                });
            } else {
                console.error("Mesaj geçmişi yüklenemedi:", data.error);
            }
        } catch (err) {
            console.error("Mesaj geçmişi hatası:", err);
        }
    }
}
async function loadBroadcastMessages(limit=50) {
    try {
        const res = await fetch(`/api/messages/broadcast?limit=${limit}`, {
            method: "GET",
            credentials: "include"
        });
        const data = await res.json();
        if(data.success) {
            data.messages.forEach(msg => {
                addMessageToUI({
                    sender: msg.sender_name,
                    content: msg.message_content
                }, msg.sender_name === currentUser.username);
            });
        }
    } catch (err) {
        console.error("Broadcast mesaj geçmişi yüklenemedi", err);
    }
}


// === 5️⃣ Mesaj gönderme ===
messageForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const content = messageInput.value.trim();
    if (!content) return;

    if (currentChat.type === "broadcast") {
        socket.emit("send_broadcast", { message: content });
    } else if (currentChat.type === "group") {
        socket.emit("send_group", { group_id: currentChat.id, content });
    } else if (currentChat.type === "private") {
        socket.emit("send_private", { receiver_id: currentChat.id, content });
    }

    // ❌ Kendi eklemesini artık burada yapmıyoruz
    messageInput.value = "";
});

// === 6️⃣ Gelen mesajları dinle ===
socket.on("receive_message", (data) => {
    console.log("📩 Yeni mesaj:", data);

    // Sadece ilgili sohbet ekranında göster
    if (
        (currentChat.type === "private" && data.sender === currentChat.name) ||
        (currentChat.type === "group" && data.group_id === currentChat.id) ||
        (currentChat.type === "broadcast")
    ) {
        addMessageToUI({
            sender: data.sender,
            content: data.message || data.content
        }, data.sender_id === currentUser.id); // kendi mesajını sağa hizala
    }
});

// === 7️⃣ Mesajı arayüze ekle ===
function addMessageToUI(data, isOwn) {
    const div = document.createElement("div");
    div.className = `p-2 my-1 rounded-lg max-w-md ${
        isOwn ? "bg-blue-500 text-white ml-auto" : "bg-gray-200 text-black mr-auto"
    }`;
    div.innerHTML = `<strong>${data.sender}:</strong> ${data.content}`;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// === 8️⃣ Broadcast modu ===
broadcastBtn.addEventListener("click", () => {
    currentChat = { type: "broadcast", id: null, name: "Tüm Kullanıcılar" };
    chatTitle.textContent = "📡 Herkese Mesaj";
    chatSubtitle.textContent = "Broadcast modu";
    messageInput.disabled = false;
    sendBtn.disabled = false;
    messagesDiv.innerHTML = "";

     loadBroadcastMessages();
});

// === 9️⃣ Grup oluşturma modalı ===
const groupModal = document.getElementById("group-modal");
const createGroupBtn = document.getElementById("create-group-btn");
const cancelGroupBtn = document.getElementById("cancel-group-btn");
const createGroupForm = document.getElementById("create-group-form");

// Modal aç/kapa
createGroupBtn.addEventListener("click", () => groupModal.classList.remove("hidden"));
cancelGroupBtn.addEventListener("click", () => groupModal.classList.add("hidden"));

// Grup oluştur
createGroupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("group-name").value.trim();
    const description = document.getElementById("group-description").value.trim();

    if (!name) return alert("Grup adı boş olamaz!");

    try {
        const res = await fetch("/api/groups/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ group_name: name, description })
        });

        const data = await res.json();

        if (data.success) {
            alert(data.message);
            groupModal.classList.add("hidden");
            document.getElementById("group-name").value = "";
            document.getElementById("group-description").value = "";
            loadGroups();
        } else {
            alert(data.error || "Bir hata oluştu");
        }
    } catch (err) {
        console.error(err);
        alert("Sunucuya bağlanılamadı");
    }
});

// === 🔟 Başlat ===
checkSession();
