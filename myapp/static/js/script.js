// script.js
document.addEventListener('DOMContentLoaded', function () {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('focus', function () {
            input.showPicker();  // This forces the date picker to appear when the input is focused
        });
    });
});
