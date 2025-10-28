document.addEventListener("DOMContentLoaded", function() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function(toastEl) {
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    });
});