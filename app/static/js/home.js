const nsBox = document.getElementById('nsBox')
const ipBox = document.getElementById('ipBox')
const doneBox = document.getElementById('doneBox')

function dragstartHandler(ev) {
  // Add different types of drag data
  ev.dataTransfer.setData("text/plain", ev.target.innerText);
  ev.dataTransfer.setData("text/html", ev.target.outerHTML);
  ev.dataTransfer.setData(
    "text/uri-list",
    ev.target.ownerDocument.location.href,
  );
}

async function getTasks() {
  const response = await fetch("/gettasks", {method: 'POST'});
  if (response.ok) {
    const data = await response.json();
    const tasks = data
    return tasks
    // deadline, name, status
  }
}

async function move_task(task, newlocation) {
  // uses task id
  arr = task.split(' ')
  console.log(arr)
  const response = await fetch('/modifytask?task=' + moving_id + '&new_location=' + newlocation)
  if (response.ok) {
    del = document.getElementById(arr[0])
    del.remove();
  }
}

let moving_task;
let moving_owned;

async function setupTasks() {
  tasks = await getTasks();
  for (let i = 0; i < tasks.length; i++) {
    document.getElementById(tasks[i][1]).addEventListener('dragstart', function(ev) {
      moving_task = tasks[i][1] + " due " + tasks[i][0]
      moving_id = tasks[i][4]
      moving_owned = tasks[i][3]
    });
  }
}

setupTasks();

nsBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

nsBox.addEventListener('drop', (ev) => {
  ev.preventDefault();
  if (moving_owned) {
    nsBox.innerHTML += 
      `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="{{ task[0] }}">
         <span>` + moving_task + `</span>
            <button class="btn btn-sm btn-outline-success" type="submit" name="edit ` + moving_task[1] + `">Edit</button>
            </div>`
  }
  else {
    nsBox.innerHTML += 
          `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="{{ task[0] }}">
         <span>` + moving_task + `</span>
         </div>`
  }
  move_task(moving_task, 'Not started');

})
ipBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

ipBox.addEventListener('drop', (ev) => {
  ev.preventDefault();
  if (moving_owned) {
    console.log(moving_task)
    ipBox.innerHTML += 
  `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="` + moving_task[0] + `">
         <span>` + moving_task + `</span>
            <button class="btn btn-sm btn-outline-success" type="submit" name="edit ` + moving_task[1] + `">Edit</button>
            </div>`
  
  }
  else {
    ipBox.innerHTML +=
      `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="{{ task[0] }}">
         <span>` + moving_task + `</span>
         </div>`
  }

  move_task(moving_task, 'In progress');
 
})

doneBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

doneBox.addEventListener('drop', function(ev) {
  ev.preventDefault();
  console.log(moving_task)
  if (moving_owned) {
    doneBox.innerHTML +=   `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="{{ task[0] }}">
         <span>` + moving_task + `</span>
            <button class="btn btn-sm btn-outline-success" type="submit" name="edit ` + moving_task[1] + `">Edit</button>
            </div>`
  }
  else {
    doneBox.innerHTML += 
          `<div class="list-group-item d-flex justify-content-between align-items-center" draggable="true" id="{{ task[0] }}">
         <span>` + moving_task + `</span>
         </div>`
  }

  move_task(moving_task, 'Done');

})


