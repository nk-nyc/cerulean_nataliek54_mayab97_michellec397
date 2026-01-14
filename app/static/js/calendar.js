const prevButton = document.getElementById("prev");
const nextButton = document.getElementById("next");
const monthelement = document.getElementById("month");
const today = new Date();

let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

const monthCodes = [1, 4, 4, 0, 2, 5, 0, 3, 6, 1, 5, 6]

const monthswithtoomanydays = ['January', 'March', 'May', 'July', 'August', 'October', 'December']


function getFirstDayOfTheWeek(month, year){
  twoDigs = year % 100;
  twoDigs = twoDigs + (Math.floor(twoDigs/4)) + 1 + monthCodes[month];
  return twoDigs % 7;
}

function initializeCalendar() {

  currentMonth = today.getMonth();
  renderCalendar(currentMonth, today.getFullYear());
}

function refreshDays(month, year) {
    date = today.getDate();

  // delete old days
  document.getElementById('days').innerHTML = '';

  // fix days of the week
  first_day = getFirstDayOfTheWeek(month, year) 
  // 0 is saturday, 1 is sunday, etc. 0 -> 5, 1 -> 6, 2 -> 0
  // plus five mod seven
  numToAdd = (first_day + 4) % 7
  console.log(numToAdd)

    //add spaces first
  for (let i = 0; i < numToAdd; i++) {
    var ul = document.getElementById('days');
    var li = document.createElement('li');
    li.appendChild(document.createTextNode('   '));
    ul.appendChild(li);
  }

  var max;
  // add new ones
  if (!monthswithtoomanydays.includes(monthNames[currentMonth]) && !(monthNames[currentMonth] == 'February')) {
    // 30 days
    max = 30
  }
  else {
    // 31
    max = 31
  }
  if (monthNames[currentMonth] == 'February') {
    max = 28
  }

  for (let i = 0; i < max; i++) {
    var newNode = document.createElement('li')
    newNode.setAttribute('id', String(i + 1))
    var parentDiv = document.getElementById('days')
    newNode.appendChild(document.createTextNode(i + 1))
    parentDiv.appendChild(newNode);
  } //add back in all elements. will add tasks to this later
  
  highlighted_item = document.getElementById(String(date));
  if (today.getMonth() == month) {
    highlighted_item.style.backgroundColor = 'lightBlue';
    highlighted_item.style.fontWeight = 'bold';
  }
}

function renderCalendar(month, year) {
  console.log(month, year)
  refreshDays(month, year);
  date = today.getDate();
  monthelement.innerText = monthNames[month] + ' ' + year;
  
}

initializeCalendar();

// scroll to other months

prevButton.addEventListener('click', () => {goBack(currentMonth, currentYear)} )
nextButton.addEventListener('click', () => {goForward(currentMonth, currentYear)} )

function goBack(month, year) {
  let newMonth;
  let newYear;
  if (month == 0) {
    newMonth = 11;
    currentMonth = 11;
    newYear = year - 1;
    currentYear = year - 1;
  }
  else {
    newMonth = month - 1;
    currentMonth = newMonth;
    newYear = year;
    currentYear = year;
  }
  renderCalendar(newMonth, newYear)
}

function goForward(month, year) {
    let newMonth;
  let newYear;
  if (month == 11) {
    newMonth = 0;
    currentMonth = 0;
    newYear = year + 1;
    currentYear = year + 1;
  }
  else {
    newMonth = month + 1;
    currentMonth = newMonth;
    newYear = year;
    currentYear = year;
  }
  renderCalendar(newMonth, newYear)
}

// create tasks functions

create = document.getElementById('create')

function createEvent() {

}

// create.addEventListener('click', createEvent)