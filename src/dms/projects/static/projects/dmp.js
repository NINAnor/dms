const url = document
  .getElementById("dmp_api_url")
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
    body: JSON.stringify({ data: survey.data }),
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
survey.readOnly = window.readOnly;
try {
  const dmp = JSON.parse(document.getElementById("dmp").textContent);
  survey.data = dmp;
} catch (e) {
  console.warn(e);
}
survey.showCompleteButton = false;
survey.onValueChanged.add(save);

survey.onTextMarkdown.add((_, options) => {
  const sanitized = DOMPurify.sanitize(marked.parse(options.text));
  if (sanitized.startsWith("<p>")) {
    options.html = sanitized.substring(3, sanitized.length - 5);
  } else {
    options.html = sanitized;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  survey.render(document.getElementById("surveyContainer"));
});

function setLocale(localeVal) {
  survey.locale = localeVal;
}
