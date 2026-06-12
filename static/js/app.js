// Toasts: autocierre, cierre manual y creacion desde eventos HTMX

function getToastStack() {
  var stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }
  return stack;
}

function wireToast(toast) {
  var hideToast = function () {
    toast.classList.add('toast-hide');
    setTimeout(function () { toast.remove(); }, 300);
  };
  toast.querySelector('.toast-close').addEventListener('click', hideToast);
  setTimeout(hideToast, 4000);
}

function createToast(message, level) {
  var toast = document.createElement('div');
  toast.className = 'toast-item toast-' + (level || '');
  toast.innerHTML = '<span></span><button type="button" class="toast-close" aria-label="Cerrar">&times;</button>';
  toast.querySelector('span').textContent = message;
  getToastStack().appendChild(toast);
  wireToast(toast);
}

// Toasts ya renderizados por el server en una recarga normal
document.querySelectorAll('.toast-item').forEach(wireToast);

// Toasts disparados por el server via HX-Trigger sin recargar
document.body.addEventListener('show_toast', function (toastEvent) {
  createToast(toastEvent.detail.message, toastEvent.detail.level);
});
