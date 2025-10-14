document.addEventListener('DOMContentLoaded', function () {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function (toastEl) {
        var delay = toastEl.getAttribute('data-bs-delay') || 4500;
        var autohide = toastEl.getAttribute('data-bs-autohide') !== 'false';
        var toast = new bootstrap.Toast(toastEl, { delay: parseInt(delay, 10), autohide: autohide });
        toast.show();
    });
});