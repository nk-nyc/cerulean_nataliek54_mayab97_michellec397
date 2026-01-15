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

async function getTasks() {
  const response = await fetch("/gettasks", {method: 'POST'});
  if (response.ok) {
    const data = await response.json();
    const tasks = data
    return tasks
  }
}

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

async function renderCalendar(month, year) {
  // setup calendar
  refreshDays(month, year);
  date = today.getDate();
  monthelement.innerText = monthNames[month] + ' ' + year;
  tasks = await getTasks() 
  // add tasks to the calendar
  console.log(tasks)
  for (let i = 0; i < tasks.length; i++) {
    if ((parseInt(tasks[i][0].slice(5, 7)) - 1) == month && parseInt(tasks[i][0].slice(0, 4)) == year) {
      console.log('e')
      let day = tasks[i][0].slice(8, 12)
      let taskName = tasks[i][1]
      let taskDate = document.getElementById(day)
      let status = tasks[i][2]
      console.log(status)
      if (status == 'Not started') {
        taskDate.innerHTML = day + `
        <div class='ns'>
          <p>` + taskName + `</p>
        </div>
        `
      } else if (status == 'In progress') {
        taskDate.innerHTML = day + `
        <div class='ip'>
          <p>` + taskName + `</p>
        </div>
        `
      } else {
        taskDate.innerHTML = day + `
        <div class='Done'>
          <p>` + taskName + `</p>
        </div>
        `        
      }

    }
  }

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

function clearBox() {
  box = document.getElementById('create_menu')
  box.innerHTML = ''
}

create = document.getElementById('create')

create.addEventListener('click', () => createEvent())

function createEvent() {
  box = document.getElementById('create_menu')
  box.innerHTML = `
  <form method='post'>
    <div>
      <h1 class="beegtext">Task name:</h1>
    </div>
    <div>
      <input class='input' type="text" name="title" class="form-control" placeholder="Task name" required autofocus>
    </div>
        <div>
      <h1 class="beegtext">Task description:</h1>
    </div>
    <div>
      <input class='big_input' type="text" name="description" class="form-control" placeholder="Task description" required autofocus>
    </div>
    <div>
      <h1 class="beegtext">Deadline:</h1>
    </div>
    <div>
      <input class='input' type="date" name="deadline" class="form-control" placeholder="Deadline" required autofocus>
    </div>
    <div>
      <h1 class="beegtext">Category:</h1>
    </div>
    <div>
      <select class='input' name="category" requred autofocus>
        <option value="chore">Chore</option>
        <option value="work">Work</option>
        <option value="errand">Errand</option>
        <option value="other">Other</option>
      </select>
    </div>
    <div>
      <h1 class="beegtext">Join Permissions:</h1>
      <p class="smoltext"><i>This determines who can join your task.</i></p>
    </div>
    <div>
      <select class='input' name="join_perms" required autofocus>
        <option value="everyone">Everyone</option>
        <option value="friends">Friends</option>
        <option value="No one">No one</option>
      </select>
    </div>
    <div>
      <h1 class="beegtext">Visibility:</h1>
      <p class="smoltext"><i>This determines who can see your task.</i></p>
    </div>
    <div>
      <select class='input' name="visibility" required autofocus>
        <option value="everyone">Everyone</option>
        <option value="friends">Friends</option>
        <option value="No one">No one</option>
      </select>
    </div>
    <button id='submit' type="submit" class="btn">Create</button>
    </form>
    </div>  
    `
}

// create.addEventListener('click', createEvent)