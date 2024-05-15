function getCookieValue(cookieName) {
    const cookies = document.cookie.split(';')
        .map(cookie => cookie.trim())
        .reduce((acc, cookie) => {
            const [name, value] = cookie.split('=');
            acc[name] = value;
            return acc;
        }, {});

    return cookies[cookieName];
};

const loggedIn = getCookieValue('logged_in');
const loginLink = document.querySelector('#loginLink');
const saveButton = document.querySelector('#saveButtonImage');
const pressedSaveButton = document.querySelector('#pressedButtonImage');
const showMyRecipesButton = document.querySelector('.my-recipes-button');

if (!loggedIn) {
    loginLink.classList.remove('hidden');
    saveButton.classList.add('hidden');
    pressedSaveButton.classList.add('hidden');
    showMyRecipesButton.classList.add('hidden');
} else {
    loginLink.classList.add('hidden');
    saveButton.classList.remove('hidden');
    showMyRecipesButton.classList.remove('hidden');
}

saveButton.addEventListener('click', function() {
    saveButton.classList.add('hidden');
    pressedSaveButton.classList.remove('hidden');

    const recipe = document.querySelector('.recipe').value;

    fetch('/save_recipe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ recipe: recipe })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                console.error('Failed to save recipe:', data.error);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

pressedSaveButton.addEventListener('click', function() {
    saveButton.classList.remove('hidden');
    pressedSaveButton.classList.add('hidden');

    fetch(`/delete_recipe`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                console.error('Failed to delete recipe:', data.error);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
