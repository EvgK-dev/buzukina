// хедер скрывается(появляется) при прокрутке

const header = document.querySelector('.header'); 
let lastScroll = 0;
const defaultOffset = 70; //расстояние, после которого исчезнет хэдер

const scrollPosition = () => window.pageYOffset || document.documentElement.scrollTop; // установление текущей позиции скролла
const containHide = () => header.classList.contains('hide'); // проверка наличия у хэдера класса hide

window.addEventListener('scroll', () => { //событие скролл
  if (scrollPosition() > lastScroll && !containHide() && scrollPosition() > defaultOffset) { 
    header.classList.add('hide');  
  } else if (scrollPosition() < lastScroll && containHide()) {
    header.classList.remove('hide');
  }

  lastScroll = scrollPosition();
})
