// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("shardsCanvas") });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create shards using BoxGeometry for uniform size
const shardCount = 50;
const shards = [];
const shardSize = 0.2;  // Smaller shard size for a more uniform look

// Shades of dark teal
const darkTealColors = [
    "#006d64", "#004f47", "#003b35", "#00564d", "#007d73"
];

// Create shards
for (let i = 0; i < shardCount; i++) {
    const geometry = new THREE.BoxGeometry(shardSize, shardSize, shardSize);
    const material = new THREE.MeshBasicMaterial({
        color: darkTealColors[Math.floor(Math.random() * darkTealColors.length)],
        wireframe: false  // For solid color shards
    });
    const shard = new THREE.Mesh(geometry, material);

    // Randomly position shards in the 3D space
    shard.position.set(
        Math.random() * 10 - 5,  // Random X position
        Math.random() * 10 - 5,  // Random Y position
        Math.random() * 10 - 5   // Random Z position
    );

    scene.add(shard);
    shards.push(shard);
}

// Camera positioning
camera.position.z = 10;

// Mouse movement listener for controlling the 360 rotation
let mouseX = 0;
let mouseY = 0;

document.addEventListener("mousemove", (event) => {
    mouseX = (event.clientX / window.innerWidth) * 2 - 1;
    mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
});

// Render the scene with animation loop
function animate() {
    requestAnimationFrame(animate);

    // Rotate the scene based on mouse movement for 360-degree effect
    scene.rotation.x = mouseY * Math.PI;  // Vertical rotation
    scene.rotation.y = mouseX * Math.PI;  // Horizontal rotation

    // Update positions of shards if needed (e.g., slight floating effect)
    shards.forEach(shard => {
        shard.rotation.x += 0.01;
        shard.rotation.y += 0.01;
    });

    renderer.render(scene, camera);
}

animate();

// Handle window resizing
window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Sign-up function
function signup() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password, email })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('signupResult').innerText = data.message || data.error;
        if (data.message === 'Sign-up successful') {
            window.location.href = '/info';
        }
    })
    .catch(error => console.error('Error:', error));
}

// Login function
function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loginResult').innerText = data.message || data.error;
        if (data.message === 'Login successful') {
            window.location.href = '/home';
        }
    })
    .catch(error => console.error('Error:', error));
}

// Update info function
function updateInfo() {
    const username = localStorage.getItem('username');
    const field1 = document.getElementById('field1').value;
    const field2 = document.getElementById('field2').value;

    fetch('/updateInfo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, field1, field2 })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('infoResult').innerText = data.message || data.error;
        if (data.message === 'Information updated successfully') {
            window.location.href = '/home';
        }
    })
    .catch(error => console.error('Error:', error));
}
