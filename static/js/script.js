document.addEventListener('DOMContentLoaded', () => {
    // Initial state
    document.getElementById('login-form').classList.add('d-none');
    document.getElementById('register-form').classList.add('d-none');
    document.getElementById('user-info').classList.add('d-none');
    showSection('accueil');
});

function loadChatHistory(courseId, type) {
    fetch(`/chat_history/${courseId}`)
    .then(response => response.json())
    .then(data => {
        const historyDiv = document.getElementById(`history-output-${type}`);
        historyDiv.innerHTML = ''; // Clear previous history
        const md = window.markdownit();
        historyDiv.innerHTML = data.map(chat => `
            <div class="message question">
                <p><strong>Question:</strong> ${md.render(chat.user_question)}</p>
                ${chat.image ? `<img src="${chat.image}" alt="Pasted image" style="max-width: 50%;">` : ''}
            </div>
            <div class="message response">
                <p><strong>Réponse:</strong> ${md.render(chat.bot_response)}</p>
            </div>
            <div class="timestamp">${chat.timestamp}</div>
        `).join('');
    });
}

function toggleForm(form) {
    if (form === 'login') {
        document.getElementById('login-form').classList.remove('d-none');
        document.getElementById('register-form').classList.add('d-none');
    } else if (form === 'register') {
        document.getElementById('login-form').classList.add('d-none');
        document.getElementById('register-form').classList.remove('d-none');
    }
}

function showSection(section) {
    const sections = document.querySelectorAll('main > section');
    sections.forEach(sec => {
        sec.classList.add('d-none');
    });
    document.getElementById(section).classList.remove('d-none');

    if (section === 'course-content') {
        // We handle the visibility of the chatbot within the loadCourse and loadExercice functions.
        return;
    }
    document.getElementById('chatbot-cours').classList.add('d-none');
    document.getElementById('chatbot-exercices').classList.add('d-none');
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
        const loginMessage = document.getElementById('login-message');
        if (data.status === 'success') {
            loginMessage.textContent = `Bienvenue, ${username} (${data.role}) - Études: ${data.etudes}`;
            document.getElementById('login-form').classList.add('d-none');
            document.getElementById('register-form').classList.add('d-none');
            document.getElementById('show-login-form').style.display = 'none';
            document.getElementById('show-register-form').style.display = 'none';
            document.getElementById('user-info').classList.remove('d-none');
            document.getElementById('user-greeting').textContent = `${username}`;
        } else {
            loginMessage.textContent = data.message;
        }
    });
}

function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const etudes = document.getElementById('register-etudes').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password, etudes: etudes })
    })
    .then(response => response.json())
    .then(data => {
        const registerMessage = document.getElementById('register-message');
        registerMessage.textContent = data.message;
    });
}

function logout() {
    document.getElementById('login-form').classList.add('d-none');
    document.getElementById('register-form').classList.add('d-none');
    document.getElementById('user-info').classList.add('d-none');
    document.getElementById('login-message').textContent = '';
    document.getElementById('user-greeting').textContent = '';
    document.getElementById('show-login-form').style.display = 'block';
    document.getElementById('show-register-form').style.display = 'block';
}

function getAllCours() {
    fetch('/all_cours')
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('cours-results');
            resultsDiv.innerHTML = data.map(course => `
                <div class="list-group-item">
                    <h3>${course.nom}</h3>
                    <p>${course.description}</p>
                    <button class="btn btn-primary" onclick="loadCourse(${course.id}, '${course.url}', '${course.nom}')">Afficher le cours</button>
                </div>
            `).join('');
        });
}

function getAllExercices() {
    fetch('/all_exercices')
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('exercices-results');
            resultsDiv.innerHTML = data.map(exercice => `
                <div class="list-group-item">
                    <h3>${exercice.nom}</h3>
                    <p>${exercice.description}</p>
                    <button class="btn btn-primary" onclick="loadExercice(${exercice.id}, '${exercice.url}', '${exercice.nom}')">Afficher l'exercice</button>
                </div>
            `).join('');
        });
}

function searchCours() {
    const query = document.getElementById('search-cours').value;
    fetch(`/search_cours?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('cours-results');
            resultsDiv.innerHTML = data.map(course => `
                <div class="list-group-item">
                    <h3>${course.nom}</h3>
                    <p>${course.description}</p>
                    <button class="btn btn-primary" onclick="loadCourse(${course.id}, '${course.url}', '${course.nom}')">Afficher le cours</button>
                </div>
            `).join('');
        });
}

function searchExercices() {
    const query = document.getElementById('search-exercices').value;
    fetch(`/search_exercices?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('exercices-results');
            resultsDiv.innerHTML = data.map(exercice => `
                <div class="list-group-item">
                    <h3>${exercice.nom}</h3>
                    <p>${exercice.description}</p>
                    <button class="btn btn-primary" onclick="loadExercice(${exercice.id}, '${exercice.url}', '${exercice.nom}')">Afficher l'exercice</button>
                </div>
            `).join('');
        });
}

function loadCourse(courseId, url, name) {
    currentCourseId = parseInt(courseId, 10);
    showSection('course-content');
    document.getElementById('course-viewer').innerHTML = `
        <object data="/cours/${url}" type="application/pdf" width="100%" height="600px"> </object>`;
    currentUrl = "/cours/" + url;
    document.getElementById('chat-output-cours').innerHTML = '';  // Clear chat output
    loadChatHistory(currentCourseId, 'cours');
    document.getElementById('chatbot-cours').classList.remove('d-none');
    document.getElementById('chatbot-exercices').classList.add('d-none');
}

function loadExercice(exerciceId, url, name) {
    currentExerciceId = parseInt(exerciceId, 10);
    showSection('course-content');
    document.getElementById('course-viewer').innerHTML = `
        <object data="/exercices/${url}" type="application/pdf" width="100%" height="600px"> </object>`;
    currentUrl = "/exercices/" + url;
    document.getElementById('chat-output-exercices').innerHTML = '';  // Clear chat output
    loadChatHistory(currentExerciceId, 'exercices');
    document.getElementById('chatbot-cours').classList.add('d-none');
    document.getElementById('chatbot-exercices').classList.remove('d-none');
}
function sendMessageCours() {
    const message = document.getElementById('chat-input-cours').value;
    const imgData = document.getElementById('pastedImage-cours').dataset.imageData ;
    if (currentCourseId === null) {
        console.error('No course selected');
        return;
    }

    console.log(`Sending message: ${message} for course_id: ${currentCourseId}, course_url: ${currentUrl}`);



    const data = { message: message, course_id: currentCourseId, course_url: currentUrl };
    if (imgData) {
        data.image = imgData;  // Add image data to the payload
    }

    document.getElementById('loading-indicator-cours').style.display = 'block';
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => console.log(response))
    .then(data => {
        // Hide the loading indicator
        document.getElementById('loading-indicator-cours').style.display = 'none';

        const chatOutput = document.getElementById('chat-output-cours');
        const md = window.markdownit();

        chatOutput.innerHTML = `
        <div class="message question">
            <p><strong>Question:</strong> ${md.render(message)}</p>
            ${imgData ? `<img src="${imgData}" alt="Pasted image" style="max-width: 50%;">` : ''}
        </div>
        <div class="message response">
            <p><strong>Réponse:</strong> ${md.render(data.response)}</p>
        </div>
        `;
        document.getElementById('chat-input-cours').value = '';  // Clear input field
        document.getElementById('pastedImage-cours').dataset.imageData = '';  // Clear pasted image
        document.getElementById('pastedImage-cours').style.display = 'none';  // Hide pasted image
        loadChatHistory(currentCourseId, 'cours');  // Reload chat history to include the new message
    })
    .catch(error => console.error('Error:', error));
    // Hide the loading indicator in case of error
    document.getElementById('loading-indicator-cours').style.display = 'none';
}

function sendMessageExercices() {
    const message = document.getElementById('chat-input-exercices').value;
    const imgData = document.getElementById('pastedImage-exercices').dataset.imageData;
    if (currentExerciceId === null) {
        console.error('No exercice selected');
        return;
    }

    console.log(`Sending message: ${message} for exercice_id: ${currentExerciceId}, exercice_url: ${currentUrl}`);

    const data = { message: message, exercice_id: currentExerciceId, exercice_url: currentUrl };
    if (imgData) {
        data.image = imgData;  // Add image data to the payload
    }

    // Show the loading indicator
    document.getElementById('loading-indicator-exercices').style.display = 'block';

    fetch('/chat_exercises', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading-indicator-exercices').style.display = 'none';

        const chatOutput = document.getElementById('chat-output-exercices');
        const feedbackOutput = document.getElementById('feedback-output-exercices');
        const recommendationsOutput = document.getElementById('recommendations-output-exercices');
        const md = window.markdownit();


        chatOutput.innerHTML = `
        <div class="message question">
            <p><strong>Question:</strong> ${md.render(message)}</p>
            ${imgData ? `<img src="${imgData}" alt="Pasted image" style="max-width: 50%;">` : ''}
        </div>`;

        feedbackOutput.innerHTML = `
        <div class="message response">
            <p><strong>Feedback:</strong> ${md.render(data.feedback)}</p>
        </div>`;

        recommendationsOutput.innerHTML = `
        <div class="message response">
            <p><strong>Recommendations:</strong> ${md.render(data.recommended)}</p>
        </div>`;

        document.getElementById('chat-input-exercices').value = '';  // Clear input field
        document.getElementById('pastedImage-exercices').dataset.imageData = '';  // Clear pasted image
        document.getElementById('pastedImage-exercices').style.display = 'none';  // Hide pasted image
        loadChatHistory(currentExerciceId, 'exercices');  // Reload chat history to include the new message
    })
    .catch(error => console.error('Error:', error));
     // Hide the loading indicator in case of error
    document.getElementById('loading-indicator-exercices').style.display = 'none';
}

function uploadCourse() {
    const fileInput = document.getElementById('course-file');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_cours', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const filename = data.filename;
            const name = document.getElementById('course-name').value;
            const description = document.getElementById('course-description').value;
            const level = document.getElementById('course-level').value;
            fetch('/add_course', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nom: name, description: description, niveau: level, url: filename })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('course-upload-message').textContent = data.message;
                getAllCours();  // Refresh the list of courses
            });
        } else {
            document.getElementById('course-upload-message').textContent = data.error;
        }
    })
    .catch(error => console.error('Error:', error));
}

function uploadExercise() {
    const fileInput = document.getElementById('exercise-file');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_exercices', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const filename = data.filename;
            const name = document.getElementById('exercise-name').value;
            const description = document.getElementById('exercise-description').value;
            const level = document.getElementById('exercise-level').value;
            fetch('/add_exercise', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nom: name, description: description, niveau: level, url: filename })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('exercise-upload-message').textContent = data.message;
                getAllExercices();  // Refresh the list of exercises
            });
        } else {
            document.getElementById('exercise-upload-message').textContent = data.error;
        }
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener('paste', function (event) {
    const items = event.clipboardData.items;
    for (let item of items) {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.getElementById('pastedImage');
                img.src = e.target.result;
                img.style.display = 'block';
                img.dataset.imageData = e.target.result;  // Store image data
            };
            reader.readAsDataURL(file);
        }
    }
});
