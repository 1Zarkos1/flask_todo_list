const ALL_TASKS_TITLE = "See all tasks below!";
const CURRENT_TASKS_TITLE = "What needs to be done!!!";

function editTask(ref) {
  event.preventDefault();
  let task = document.querySelector(`#task-${ref}`);
  let form = document.querySelector("#main-form");
  let title = task.querySelector("#title").innerHTML;
  let date = task
    .querySelector(`#due-${ref}`)
    .innerHTML.split(" ")
    .slice(2, 4)
    .join("T")
    .slice(0, -3);
  let description = task.querySelector("#description").innerHTML;

  form.querySelector("legend").innerHTML = `Edit task №${ref}`;
  form.querySelector("#title-form").value = title;
  form.querySelector("#date-form").setAttribute("value", date);
  form.querySelector("#description-form").value = description;
  form.querySelector("#hidden_id").value = ref;
}

function assignRemainingTime(elem, dueTime) {
  elem.setAttribute(
    "title",
    moment(dueTime, "YYYY-MM-DD HH:mm:ss", true).fromNow()
  );
}

function getTasks(check, url) {
  let listTitle = document.querySelector("#list-title");
  if (check.checked) {
    listTitle.innerHTML = CURRENT_TASKS_TITLE;
  } else {
    listTitle.innerHTML = ALL_TASKS_TITLE;
  }
  let response = fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accepts: "text/html",
    },
    body: JSON.stringify(check.checked),
  })
    .then((response) => response.text())
    .then((data) => {
      let main = document.querySelector("#main-todos");
      main.innerHTML = data;
    })
    .catch((error) => console.log(error));
}

function deleteTask(ref, url) {
  event.preventDefault();
  fetch(ref.href, {
    method: "GET",
  })
    .then(() => {
      let check = document.querySelector("#done");
      getTasks(check, url);
    })
    .catch((error) => alert(error));
}

function completeTask(ref, url) {
  event.preventDefault();
  fetch(ref.href, {
    method: "GET",
  })
    .then(() => {
      let check = document.querySelector("#done");
      getTasks(check, url);
    })
    .catch((error) => alert(error));
}
