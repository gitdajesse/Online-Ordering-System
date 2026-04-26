document.addEventListener("DOMContentLoaded", function() {
    // Get all remove buttons
    const removeButtons = document.querySelectorAll(".remove-btn");
    const modalItemId = document.getElementById("modalItemId");
    const confirmRemoveModal = document.getElementById("confirmRemoveModal");
    const removeForm = document.getElementById("removeForm");

    // Check if elements exist
    if (!removeButtons.length) {
        console.log("No remove buttons found");
        return;
    }

    if (!modalItemId) {
        console.error("modalItemId element not found");
        return;
    }

    if (!confirmRemoveModal) {
        console.error("confirmRemoveModal element not found");
        return;
    }

    if (!removeForm) {
        console.error("removeForm element not found");
        return;
    }

    // Add click event to each remove button
    removeButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            // Get the item ID from data-id attribute
            const itemId = this.getAttribute("data-id");

            if (!itemId) {
                console.error("No item ID found on button:", this);
                return;
            }

            // Trim any whitespace from the item ID
            const cleanItemId = itemId.trim();

            // Set the item ID in the modal form
            modalItemId.value = cleanItemId;

            // Show the modal
            const modal = new bootstrap.Modal(confirmRemoveModal);
            modal.show();

            console.log("Modal shown for item ID:", cleanItemId); // Debug log
        });
    });

    // Optional: Add logging to see when modal form submits
    removeForm.addEventListener("submit", function(e) {
        console.log("Remove form submitting with item_id:", modalItemId.value);
    });
});

function closeModal() {
    const modalElement = document.getElementById('confirmRemoveModal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}
