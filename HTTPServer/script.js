var slider = document.getElementById("RotationalSpeeds");

function sendData() {
  var sliderValue = document.getElementById("RotationalSpeeds").value;
  fetch("/slider", {
    method: "POST",
    body: sliderValue
  })
}

function sendStop() {
  var sliderValue = 0;
  fetch("/slider", {
    method: "POST",
    body: sliderValue
  })
}

function sendDir() {
  fetch("/change_direction")
}

function sendZero() {
  fetch("/change_position")
}

function updateCurrentRPM() {
  fetch("/current_rpm")
    .then(response => response.text())
    .then(data => {
      const currentRPM = document.getElementById("current-rpm");
      currentRPM.innerText = data;
    })
    .catch(error => {
      console.log("Error updating current RPM:", error);
    }); 
}

function updateDesiredRPM() {
  fetch("/desired_rpm")
    .then(response => response.text())
    .then(data => {
      const desiredRPM = document.getElementById("desired-rpm");
      desiredRPM.innerText = data;
    })
    .catch(error => {
      console.log("Error updating current RPM:", error);
    }); 
}

function updateCurrentPosition() {
  fetch("/current_position")
    .then(response => response.text())
    .then(data => {
      const image = document.querySelector(".imagePos");
      const Position = parseFloat(data);
      image.style.transform = `rotate(${Position}deg)`;
    })
    .catch(error => {
      console.log("Error updating current Position:", error);
    });
}

updateCurrentRPM();
updateDesiredRPM();
updateCurrentPosition();

setInterval(updateCurrentRPM, 1000);
setInterval(updateDesiredRPM, 1000);
setInterval(updateCurrentPosition, 25);
