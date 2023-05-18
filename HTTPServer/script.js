function sendData() {
  const sliderValue = document.getElementById("myRange").value;
  fetch("/slider", {
    method: "POST",
    body: sliderValue.toString()
  });
}

function sendStop() {
  fetch("/slider", {
    method: "POST",
    body: "0"
  });
}

function sendDir() {
  fetch("/change_direction");
}

function sendZero() {
  fetch("/change_position");
}

function updateRPM(elementId, url) {
  fetch(url)
    .then(response => response.text())
    .then(data => {
      const element = document.getElementById(elementId);
      element.textContent = data;
    })
    .catch(error => {
      console.log(`Error updating ${elementId}:`, error);
    });
}

function updateCurrentRPM() {
  updateRPM("current-rpm", "/current_rpm");
}

function updateDesiredRPM() {
  updateRPM("desired-rpm", "/desired_rpm");
}

function updateCurrentPosition() {
  fetch("/current_position")
    .then(response => response.text())
    .then(data => {
      const image = document.querySelector(".image-pos");
      const position = parseFloat(data);
      image.style.transform = `rotate(${position}deg)`;
    })
    .catch(error => {
      console.log("Error updating current position:", error);
    });
}

function setupSlider() {
  const slider = document.getElementById("myRange");
  const output = document.getElementById("demo");
  output.innerHTML = slider.value;

  slider.oninput = function() {
    output.innerHTML = this.value;
  };
}

// Call the functions initially to update the current values
updateCurrentRPM();
updateDesiredRPM();
updateCurrentPosition();
setupSlider();

// Call the functions every 2 seconds to keep updating the values
setInterval(updateCurrentRPM, 1000);
setInterval(updateDesiredRPM, 1000);
setInterval(updateCurrentPosition, 25);

// Add event listeners to the buttons
document.getElementById("sendButton").addEventListener("click", sendData);
document.getElementById("stopButton").addEventListener("click", sendStop);
document.getElementById("dirButton").addEventListener("click", sendDir);
document.getElementById("zeroButton").addEventListener("click", sendZero);
