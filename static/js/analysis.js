document.addEventListener('DOMContentLoaded', function() {
    const indicatorCheckboxes = document.querySelectorAll('input[name="indicators"]');
    const submitButton = document.querySelector('form[action*="run"] button[type="submit"]');

    if (indicatorCheckboxes.length > 0 && submitButton) {
        function updateSubmitButton() {
            const checkedCount = document.querySelectorAll('input[name="indicators"]:checked').length;
            submitButton.disabled = checkedCount === 0;
        }

        indicatorCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSubmitButton);
        });

        updateSubmitButton();
    }
});
