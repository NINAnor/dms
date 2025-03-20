const url = document
  .getElementById("project_api_url")
  .textContent.replaceAll('"', "");
const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

function save(survey) {
  fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    mode: "same-origin",
    body: JSON.stringify({ dmp: survey.data }),
  })
    .then((response) => {
      if (response.ok) {
        Toastify({
          text: "Saved",
          duration: 3000,
          newWindow: true,
          close: true,
          gravity: "top",
          position: "center",
          stopOnFocus: true,
        }).showToast();
      } else {
        Toastify({
          text: "Error",
          duration: 3000,
          newWindow: true,
          close: true,
          gravity: "top",
          position: "center",
          stopOnFocus: true,
        }).showToast();
      }
    })
    .catch((error) => {
      // Handle error
    });
}

const config = JSON.parse(document.getElementById("dmp-config").textContent);
const survey = new Survey.Model(config);
try {
  const dmp = JSON.parse(document.getElementById("dmp").textContent);
  survey.data = dmp;
} catch (e) {
  console.warn(e);
}
survey.showCompleteButton = false;
survey.onValueChanged.add(save);

// survey.onComplete.add((survey) => {
//   save(survey.data);
// });

document.addEventListener("DOMContentLoaded", function () {
  survey.render(document.getElementById("surveyContainer"));
});
