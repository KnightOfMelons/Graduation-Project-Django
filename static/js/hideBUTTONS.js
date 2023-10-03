const secondline = document.querySelector('#secondLINE');
const actionBtn = document.querySelector('#actionBtn');

actionBtn.addEventListener('click', function() {
//   Если кнопки уже скрыты, то показываем их
  if (secondline.classList.contains('hide')) {
    secondline.classList.remove('hide');
    actionBtn.innerHTML = 'Less';
  } else {
//     Иначе скрываем кнопки
    secondline.classList.add('hide');
    actionBtn.innerHTML = 'More';
  }
});