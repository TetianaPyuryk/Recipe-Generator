const recipeContainer = document.querySelector('.table-container');

recipeContainer.addEventListener('click', function(event) {
    if (event.target.classList.contains('recipe-cell')) {
        const recipeId = event.target.dataset.recipeId;
        const recipeCell = event.target;

        if (!recipeCell.dataset.loaded) {
            fetch(`/my_recipes/${recipeId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Failed to get directions:', data.error);
                } else {
                    event.target.innerHTML += `<br>Directions:<br>${data.directions}`;
                    recipeCell.dataset.loaded = true;
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            const directionsIndex = recipeCell.innerHTML.indexOf('<br>Directions:<br>');
            if (directionsIndex !== -1) {
                recipeCell.innerHTML = recipeCell.innerHTML.substring(0, directionsIndex);
                delete recipeCell.dataset.loaded;
            }
        }
    }
});