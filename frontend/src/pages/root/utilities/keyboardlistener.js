import Cookies from "js-cookie";

let for_back_velocity = 0;
let left_right_velocity = 0;
let up_down_velocity = 0;
let yaw_velocity = 0;
let vel_speed = 10;

document.addEventListener("keyup", function (event) {
  if (
    Cookies.get("relayName") !== undefined &&
    Cookies.get("droneName") !== undefined
  ) {
    switch (event.key.toLowerCase()) {
      case "w":
        for_back_velocity = 0;
        break;

      case "s":
        for_back_velocity = 0;
        break;

      case "a":
        left_right_velocity = 0;
        break;

      case "d":
        left_right_velocity = 0;
        break;

      case "arrowup":
        up_down_velocity = 0;
        break;

      case "arrowdown":
        up_down_velocity = 0;
        break;

      case "arrowleft":
        yaw_velocity = 0;
        break;

      case "arrowright":
        yaw_velocity = 0;
        break;
    }

    sendCMDToBackend([
      for_back_velocity,
      left_right_velocity,
      up_down_velocity,
      yaw_velocity,
    ]);
  }
});

document.addEventListener("keydown", function (event) {
  if (
    Cookies.get("relayName") !== undefined &&
    Cookies.get("droneName") !== undefined
  ) {
    switch (event.key.toLowerCase()) {
      case "w":
        for_back_velocity = vel_speed;
        break;

      case "s":
        for_back_velocity = -vel_speed;
        break;

      case "a":
        left_right_velocity = -vel_speed;
        break;

      case "d":
        left_right_velocity = vel_speed;
        break;

      case "arrowup":
        up_down_velocity = vel_speed;
        break;

      case "arrowdown":
        up_down_velocity = -vel_speed;
        break;

      case "arrowleft":
        yaw_velocity = -vel_speed;
        break;

      case "arrowright":
        yaw_velocity = vel_speed;
        break;
    }
    if (event.key.toLowerCase() === "t") {
      droneTakeoff();
    } else if (event.key.toLowerCase() === "l"){
      droneLand();
    } else {
      sendCMDToBackend([
        for_back_velocity,
        left_right_velocity,
        up_down_velocity,
        yaw_velocity,
      ]);
    }
  }
});

function sendCMDToBackend(cmd_velocity) {
  fetch("http://localhost:8000/v1/api/frontend/drone/new_command", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      relay_name: Cookies.get("relayName"),
      drone_name: Cookies.get("droneName"),
      cmd: cmd_velocity,
    }),
  });
}

function droneTakeoff() {
  fetch("http://localhost:8000/v1/api/frontend/drone/takeoff", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: Cookies.get("droneName"),
      parent: Cookies.get("relayName"),
    }),
  });
}

function droneLand() {
  fetch("http://localhost:8000/v1/api/frontend/drone/land", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: Cookies.get("droneName"),
      parent: Cookies.get("relayName"),
    }),
  });
}

function isDroneAirbron() {}
