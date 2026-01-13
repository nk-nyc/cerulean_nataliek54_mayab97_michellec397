const prevButton = document.getElementById("prev");

const nextButton = document.getElementById("next");

const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

let currentYear;

let currentMonth;

let selectedDate = null;

const today = new Date();


function initializeCalendar() {

  currentYear = today.getFullYear();
  currentMonth = today.getMonth();
  renderCalendar();
}

function renderCalendar() {
  date = today.getDate();
  console.log(date);
  highlighted_item = document.getElementById(String(date));
  highlighted_item.style.backgroundColor = 'lightBlue';
}

initializeCalendar();
