const creatorOptions = {
  showLogicTab: true,
  isAutoSave: true,
};
const creator = new SurveyCreator.SurveyCreator(creatorOptions);
creator.text = JSON.stringify(
  JSON.parse(document.getElementById("survey-config").textContent)
);
document.addEventListener("DOMContentLoaded", function () {
  creator.render(document.getElementById("surveyCreator"));
});

creator.saveSurveyFunc = (saveNo, callback) => {
  callback(saveNo, true);
  saveSurveyJson("update/", creator.JSON, saveNo, callback);
};

function saveSurveyJson(url, json, saveNo, callback) {
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(json),
  })
    .then((response) => {
      if (response.ok) {
        callback(saveNo, true);
      } else {
        callback(saveNo, false);
      }
    })
    .catch((error) => {
      callback(saveNo, false);
    });
}
