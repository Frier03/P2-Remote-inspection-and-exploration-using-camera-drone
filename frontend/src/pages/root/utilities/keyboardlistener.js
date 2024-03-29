import Cookies from "js-cookie";
import config from "../../../config.json"
let for_back_velocity = 0;
let left_right_velocity = 0;
let up_down_velocity = 0;
let yaw_velocity = 0;
let vel_speed = 50;

document.addEventListener("keyup", function (event) {
  if (
    Cookies.get("relayName") !== undefined &&
    Cookies.get("droneName") !== undefined
  ) {
    switch (event.key.toLowerCase()) {
      case "a":
        for_back_velocity = 0;
        break;

      case "d":
        for_back_velocity = 0;
        break;

      case "w":
        left_right_velocity = 0;
        break;

      case "s":
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

      default:
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
      case "a":
        for_back_velocity = vel_speed;
        break;

      case "d":
        for_back_velocity = -vel_speed;
        break;

      case "w":
        left_right_velocity = vel_speed;
        break;

      case "s":
        left_right_velocity = -vel_speed;
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

      default:
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
  fetch(`http://${config.BASE_URL}/v1/api/frontend/drone/new_command`, {
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
  fetch(`http://${config.BASE_URL}/v1/api/frontend/drone/takeoff`, {
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
  fetch(`http://${config.BASE_URL}/v1/api/frontend/drone/land`, {
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

export default droneTakeoff
