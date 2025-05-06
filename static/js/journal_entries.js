document.addEventListener('DOMContentLoaded', function() {
    // Edit Button functionality
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const entryId = this.getAttribute('data-id');
            
            // Ensure elements exist before interacting with them
            const textElement = document.getElementById(`text-${entryId}`);
            const editElement = document.getElementById(`edit-${entryId}`);
            const saveButton = document.querySelector(`#entry-${entryId} .save-btn`);

            if (textElement && editElement && saveButton) {
                textElement.style.display = 'none';
                editElement.style.display = 'block';
                this.style.display = 'none';
                saveButton.style.display = 'inline-block';
            }
        });
    });

    // Save Button functionality
    document.querySelectorAll('.save-btn').forEach(button => {
        button.addEventListener('click', function() {
            const entryId = this.getAttribute('data-id');
            const updatedText = document.getElementById(`edit-${entryId}`).value;
            
            // Send AJAX request to save the updated entry
            fetch(`/accounts/update-journal/${entryId}/`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF token from the form
                },
                body: JSON.stringify({ entry: updatedText })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the text and hide the edit box
                    const textElement = document.getElementById(`text-${entryId}`);
                    textElement.innerText = updatedText;  // Set the updated text to be shown
                    textElement.style.display = 'block';  // Show the updated text

                    // Hide the edit box and save button
                    document.getElementById(`edit-${entryId}`).style.display = 'none';
                    button.style.display = 'none';

                    // Show the edit button again
                    document.querySelector(`#entry-${entryId} .edit-btn`).style.display = 'inline-block';
                } else {
                    alert('Failed to save the entry.');
                }
            })
            .catch(error => console.error('Error saving entry:', error));
        });
    });

    // Delete Button functionality
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const entryId = this.getAttribute('data-id');

            // Send AJAX request to delete the entry
            if (confirm('Are you sure you want to delete this entry?')) {
                fetch(`/accounts/delete-journal/${entryId}/`, { 
                    method: 'POST',  // Ensure this is a POST request
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF token from the form
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(`entry-${entryId}`).remove();
                    } else {
                        alert('Failed to delete the entry.');
                    }
                })
                .catch(error => console.error('Error deleting entry:', error));
            }
        });
    });
});
