// Менеджер календаря бронирования: отображение, выбор дат, проверка занятости, расчет стоимости

class CalendarManager {
    constructor(containerId) {
      this.containerId = containerId;
      this.selectedStartDate = null;
      this.selectedEndDate = null;
      this.today = new Date();
      
      this.currentDate = new Date();

      this.reservedDates = null;  
      this.init();
    }

    // Инициализация календаря, установка слушателей событий и загрузка занятых дат
    init() {
      this.getReservedDates();
      this.createCalendar(this.today.getFullYear(), this.today.getMonth());
      this.handleManualDateChange();
  
      document.getElementById(`checkInDate_${this.containerId}`).addEventListener('change', () => this.calculateSelectedDays());
      document.getElementById(`checkOutDate_${this.containerId}`).addEventListener('change', () => this.calculateSelectedDays());
      document.getElementById(`prevMonth_${this.containerId}`).addEventListener('click', () => this.prevMonth());
      document.getElementById(`nextMonth_${this.containerId}`).addEventListener('click', () => this.nextMonth());
      document.getElementById(`clearSelection_${this.containerId}`).addEventListener('click', () => this.clearSelection());
    }

    // Генерация календаря на выбранный месяц и год с учетом занятых дат
    createCalendar(year, month) {
      const container = document.getElementById('calendar_' + this.containerId);
      container.innerHTML = '';
    
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDayOfMonth = new Date(year, month, 1).getDay();
      const lastDayOfMonth = new Date(year, month + 1, 0).getDay();
    
      const monthNames = [
        "Январь", "Февраль", "Март",
        "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь",
        "Октябрь", "Ноябрь", "Декабрь"
      ];
    
      const header = document.createElement('div');
      header.classList.add('calendar-header');
      header.innerHTML = `
          <span>${monthNames[month]} ${year}</span>
          <button class="select_month_button" id="prevMonth_${this.containerId}">Пред.</button>
          <button class="select_month_button" id="nextMonth_${this.containerId}">След.</button>
      `;
      container.appendChild(header);
    
      const daysContainer = document.createElement('div');
      daysContainer.classList.add('calendar-days');
    
      let dayOfWeek = (firstDayOfMonth - 1 + 7) % 7;
    
      const reservedDatesSet = new Set(this.reservedDates);
    
      for (let i = 0; i < dayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.classList.add('day', 'empty-day');
        daysContainer.appendChild(emptyDay);
      }
    
      const today = new Date();
      for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.classList.add('day');
        dayElement.textContent = day;
    
        const formattedDate = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        dayElement.setAttribute('data-day', formattedDate);
    
        if (dayOfWeek === 5 || dayOfWeek === 6) {
          dayElement.classList.add('holiday');
        }
    
        dayElement.onclick = () => this.selectDate(year, month, day);
        daysContainer.appendChild(dayElement);
    
        if (reservedDatesSet.has(formattedDate)) {
          dayElement.classList.add('booked');
        }
    
        if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
          dayElement.classList.add('selected', 'current-date');
        }
    
        
        if (dayElement.classList.contains('booked')) {
          dayElement.style.backgroundColor = 'white';
          dayElement.style.cursor = 'default';
          dayElement.onclick = null;
          dayElement.style.color = 'red';
          dayElement.style.textDecoration = 'line-through';
        }
        
        dayOfWeek = (dayOfWeek + 1) % 7;
      }
    
      for (let i = (lastDayOfMonth + 1 + 6) % 7; i < 6; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.classList.add('day', 'empty-day');
        daysContainer.appendChild(emptyDay);
      }
    
      container.appendChild(daysContainer);
    }
    
    // Извлекает список забронированных дат из DOM и сохраняет в виде массива
    getReservedDates() {
      const reservedDatesList = document.querySelectorAll(`.reserved_dates_${this.containerId} li`);
      const reservedDatesArray = Array.from(reservedDatesList).map(li => li.textContent.trim());
      this.reservedDates =  reservedDatesArray;
      var element = document.querySelector(`.reserved_dates_${this.containerId}`);
      element.remove();
    }
    
    // Обработка выбора даты пользователем (выезд/заезд), проверка валидности
    selectDate(year, month, day) {
      const selectedDate = new Date(year, month, day + 1);
      const today = new Date();
    
      if (selectedDate < today) {
        alert('Выберите дату, начиная с сегодняшней');
        return;
      }
    
      const formattedDate = selectedDate.toISOString().split('T')[0];
    
      const allDayElements = document.querySelectorAll(`#calendar_${this.containerId} .day`);
      allDayElements.forEach(element => element.classList.remove('user_selected'));
    
      const selectedDayElement = document.querySelector(`#calendar_${this.containerId} .day[data-day="${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}"]`);
    
      if (selectedDayElement) {
        if (selectedDayElement.classList.contains('booked')) {
          return;
        }
      }
    
      if (!this.selectedStartDate) {
        this.selectedStartDate = selectedDate;
        document.getElementById(`checkInDate_${this.containerId}`).value = formattedDate;
        document.getElementById(`checkOutDate_${this.containerId}`).value = '';
      } else if (!this.selectedEndDate && this.selectedStartDate < selectedDate) {
        this.selectedEndDate = selectedDate;
        document.getElementById(`checkOutDate_${this.containerId}`).value = formattedDate;
        this.calculateSelectedDays();
      } else if (selectedDate < this.selectedStartDate && selectedDate >= today) {
        this.selectedStartDate = selectedDate;
        document.getElementById(`checkInDate_${this.containerId}`).value = formattedDate;
        this.calculateSelectedDays();
      } else if (selectedDate > this.selectedStartDate && selectedDate >= today) {
        this.selectedEndDate = selectedDate;
        document.getElementById(`checkOutDate_${this.containerId}`).value = formattedDate;
        this.calculateSelectedDays();
      }
    }
    
    // Обработчики переключения месяцев назад и вперед
    prevMonth() {
      this.currentDate.setMonth(this.currentDate.getMonth() - 1);
      this.createCalendar(this.currentDate.getFullYear(), this.currentDate.getMonth());
      this.attachEventListeners();
      setupClickHandler()
    }
    
    nextMonth() {
      this.currentDate.setMonth(this.currentDate.getMonth() + 1);
      this.createCalendar(this.currentDate.getFullYear(), this.currentDate.getMonth());
      this.attachEventListeners();
      setupClickHandler()
    }
    
    attachEventListeners() {
      document.getElementById(`prevMonth_${this.containerId}`).addEventListener('click', () => this.prevMonth());
      document.getElementById(`nextMonth_${this.containerId}`).addEventListener('click', () => this.nextMonth());
    }
    
  
    // Проверка введенных дат и отображение ошибок
    handleManualDateChange() {
      const checkInDateInput = document.getElementById(`checkInDate_${this.containerId}`);
      const checkOutDateInput = document.getElementById(`checkOutDate_${this.containerId}`);
      
      let checkInErrorShown = false;
      let checkOutErrorShown = false;
  
      checkInDateInput.addEventListener('input', () => {
        const selectedDate = new Date(checkInDateInput.value);

        const year = selectedDate.getFullYear();
        const month = (selectedDate.getMonth() + 1).toString().padStart(2, '0');
        const day = selectedDate.getDate().toString().padStart(2, '0');

        const formattedDate = `${year}-${month}-${day}`;

        if (this.reservedDates && this.reservedDates.includes(formattedDate)) {
          alert('Эту дату заезда уже кто-то забронировал');
          checkInDateInput.value = '';
          return;
        } 

        if (isNaN(selectedDate.getTime()) || selectedDate < this.today || (checkOutDateInput.value && selectedDate >= new Date(checkOutDateInput.value))) {
          if (!checkInErrorShown) {
            alert('Выберите корректную дату заезда');
            checkInDateInput.value = '';
          }
          return;
        }
      });
  
      checkOutDateInput.addEventListener('input', () => {
        const selectedDate = new Date(checkOutDateInput.value);
  
        if (isNaN(selectedDate.getTime()) || selectedDate < this.today || (checkInDateInput.value && selectedDate <= new Date(checkInDateInput.value))) {
          if (!checkOutErrorShown) {
            alert('Выберите корректную дату выезда');
            checkOutDateInput.value = '';
          }
          return;
        }
      });
    }
  
    // Очистка выбранных пользователем дат и полей формы
    clearSelection() {
      this.selectedStartDate = null;
      this.selectedEndDate = null;
  
      document.getElementById(`checkInDate_${this.containerId}`).value = '';
      document.getElementById(`checkOutDate_${this.containerId}`).value = '';
      document.getElementById(`selectedDays_${this.containerId}`).value = '';
      document.getElementById(`prepayment_${this.containerId}`).value = '';
    }
  
  // Вычисление количества выбранных дней и расчёт стоимости на основе цены за день
  calculateSelectedDays() {
    const checkInDate = new Date(document.getElementById(`checkInDate_${this.containerId}`).value);
    const checkOutDate = new Date(document.getElementById(`checkOutDate_${this.containerId}`).value);
  
    if (!isNaN(checkInDate) && !isNaN(checkOutDate) && checkOutDate >= checkInDate) {
      const timeDiff = checkOutDate.getTime() - checkInDate.getTime();
      const selectedDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
      document.getElementById(`selectedDays_${this.containerId}`).value = selectedDays;
  
      const weekdayPriceElement = document.getElementById(`selectedDays_${this.containerId}`);
      const weekdayPriceAttribute = weekdayPriceElement.getAttribute("data-weekday-price");
  
      const match = weekdayPriceAttribute.match(/\d+/);
  
      if (match) {
        const weekdayPrice = parseFloat(match[0]);
        const totalCost = Math.round(selectedDays * weekdayPrice * 0.5);

        document.getElementById(`prepayment_${this.containerId}`).value = totalCost + " " + "б.р.";
      } else {
        document.getElementById(`prepayment_${this.containerId}`).value = '';
      }
  
    } else {
      document.getElementById(`selectedDays_${this.containerId}`).value = '';
    }
  }
}

// Создание экземпляров календаря для всех контейнеров на странице
document.addEventListener('DOMContentLoaded', function () {
  const calendarElements = document.querySelectorAll('.calendar');
  const calendarIds = [];
  calendarElements.forEach(function (element) {
      const id = element.id.replace(/\D/g, ''); 
      if (id) {
          calendarIds.push(id);
      }
  });

  calendarIds.forEach(function (id) {
      new CalendarManager(id);
  });
});
  
  document.addEventListener('DOMContentLoaded', function () {
    setupClickHandler();
  });
   
  // Настройка отображения формы бронирования при клике на дату
  function setupClickHandler() {
    var dayElements = document.querySelectorAll('.day');
    dayElements.forEach(function (dayElement) {
      dayElement.addEventListener('click', function () {
        var calendarElement = dayElement.closest('.calendar_conteiner');
  
        if (calendarElement) {
          var bookingFormElementInCalendar = calendarElement.querySelector('.booking-form');
  
          if (bookingFormElementInCalendar && bookingFormElementInCalendar.classList.contains('none')) {
            var allBookingFormElements = document.querySelectorAll('.booking-form.visible');
            allBookingFormElements.forEach(function (form) {
              form.classList.remove('visible');
              form.classList.add('none');
            });
  
            bookingFormElementInCalendar.classList.remove('none');
  
            setTimeout(function () {
              bookingFormElementInCalendar.classList.add('visible');
            }, 10);
          }
        }
      });
    });
  }

// копируем текст в буфер обмена
function copyToClipboard() {
  var textToCopy = document.querySelector('.booking_erip').innerText;
  var textarea = document.createElement('textarea');
  textarea.value = textToCopy;

  document.body.appendChild(textarea);  
  textarea.select(); 
  document.execCommand('copy'); 
  document.body.removeChild(textarea);
  alert('Текст скопирован в буфер обмена');
}

