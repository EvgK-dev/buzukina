class Slider {
  constructor(sliderElement) {
    this.sliderElement = sliderElement;
    this.pagination = sliderElement.nextElementSibling; 
    this.currentIndex = 0;
    this.startX = 0;
    this.isDragging = false;
    this.autoSlideTimeout;

    this.init();
  }

  init() {
    this.createPagination();
    this.updateSlider();
    this.updatePagination();

    this.sliderElement.addEventListener('mousedown', this.handleDragStart.bind(this));
    this.sliderElement.addEventListener('touchstart', this.handleDragStart.bind(this));
    document.addEventListener('mouseup', this.handleDragEnd.bind(this));
    document.addEventListener('touchend', this.handleDragEnd.bind(this));
    document.addEventListener('mousemove', this.handleDragMove.bind(this));
    document.addEventListener('touchmove', this.handleDragMove.bind(this));

    this.startAutoSlide();
  }

  createPagination() {
    const dots = this.sliderElement.children.length;

    for (let i = 0; i < dots; i++) {
      const dot = document.createElement('div');
      dot.classList.add('dot');
      dot.addEventListener('click', () => this.goToSlide(i));
      this.pagination.appendChild(dot);
    }
  }

  updateSlider() {
    this.sliderElement.style.transform = `translateX(${-this.currentIndex * 340}px)`;
  }

  updatePagination() {
    const dots = this.pagination.children;

    for (let i = 0; i < dots.length; i++) {
      dots[i].classList.toggle('active', i === this.currentIndex);
    }
  }

  goToSlide(index) {
    if (index >= 0 && index < this.sliderElement.children.length && index !== this.currentIndex) {
      this.currentIndex = index;
      this.updateSlider();
      this.updatePagination();

    }
  }

  handleDragStart(e) {
    e.preventDefault();
    this.isDragging = true;
    this.startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
  }

  handleDragEnd() {
    this.isDragging = false;
  }

  handleDragMove(e) {
    if (!this.isDragging) return;

    const currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
    const deltaX = currentX - this.startX;

    if (deltaX > 50 && this.currentIndex > 0) {
      this.goToSlide(this.currentIndex - 1);
      this.startX = currentX;
    } else if (deltaX < -50 && this.currentIndex < this.sliderElement.children.length - 1) {
      this.goToSlide(this.currentIndex + 1);
      this.startX = currentX;
    }
  }

  startAutoSlide() {
    this.autoSlideTimeout = setTimeout(() => {
      const nextIndex = (this.currentIndex + 1) % this.sliderElement.children.length;
      this.goToSlide(nextIndex);
      this.startAutoSlide();
    }, 10000);
  }

}

document.querySelectorAll('.slider').forEach(sliderElement => new Slider(sliderElement));
