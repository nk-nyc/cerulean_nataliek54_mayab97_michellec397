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
    console.log(tasks)
    return tasks
    // deadline, name, status
  }
}

tasks = getTasks();
for (let i = 0; i < tasks.length; i++) {
  document.getElementById(task[1]).addEventListener('dragstart', dragstartHandler);
}

nsBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

nsBox.addEventListener('drop', (ev) => {
  ev.preventDefault();
  const data = ev.dataTransfer.getData('text/plain')
  ev.nsBox.append(data);
})
ipBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

ipBox.addEventListener('drop', (ev) => {
  ev.preventDefault();
  const data = ev.dataTransfer.getData('text/plain')
  ipBox.innerText = (data);
})

doneBox.addEventListener('dragover', (ev) => {
  ev.preventDefault();
})

doneBox.addEventListener('drop', (ev) => {
  ev.preventDefault();
  const data = ev.dataTransfer.getData('text/plain')
  console.log(data)
  doneBox.innerText = (data);
})
