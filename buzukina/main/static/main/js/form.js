// Плавающие label для input — поднимаются при вводе, опускаются при очистке

const inputs = document.querySelectorAll('input');

  inputs.forEach((input) => {
    const label = input.nextElementSibling;

    input.addEventListener('input', () => {
      label.style.transition = 'none';
      label.style.top = '-10px';
      label.style.fontSize = '12px';
      label.style.color = '#000';
    });

    input.addEventListener('blur', () => {
      if (!input.value) {
        label.style.transition = '0.3s';
        label.style.top = '10px';
        label.style.fontSize = '14px';
        label.style.color = '#888';
      }
  });
});

