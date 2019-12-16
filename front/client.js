// The IP of URL at which the server is located
const SERVER_LOCATION = "172.18.0.142:5000";

// The time after which we stop trying to reach the server (in milliseconds)
const CONNECTION_TIMEOUT = 4000;

// Whether or not we should attempt to reconnect upon failure
const CONNECTION_RETRY = false;

// Connection status
const CONNECTION_STATUS = {CLOSED: 0, OPEN: 1, CONNECTING: 2};
let connectionStatus = CONNECTION_STATUS.CONNECTING;

// Display constants
const CANVAS_BG_COLOR = "rgb(40, 40, 40)";

// Payment
const PAYMENT_BLOCKING_DURATION = 2500;
let processingPayment = false;

let pictureCanvas = null;
let imgScale = 0;
let lastLabelsReceived = [];

let camImg = new Image();
camImg.onload = refreshCanvasDisplay;

// Stores the color for each label (generated when discovering a new label)
let labelColors = {};
// Stores item info for each label (price and nutritional data)
let labelInfo = {};

// When everything is loaded, register some events and get the canvas from the document
$(document).ready(() => {
  $("#button-pay").click(pay);

  pictureCanvas = $("#picture canvas")[0];

  onWindowResize();
  window.addEventListener("resize", onWindowResize);
});

// Connect to the server
connectToServer(SERVER_LOCATION, onWsMessageReceived);

/**
 * Updates the canvas when the window is resized
 */
function onWindowResize() {
  if(pictureCanvas) {
    let canvasContainer = $("#picture");
    pictureCanvas.width = canvasContainer.width();
    pictureCanvas.height = canvasContainer.height();
    refreshCanvasDisplay();
  }
}

/**
 * Sends a message through a given WebSocket.
 * @param {WebSocket} socket - The WebSocket instance to send the message through
 * @param {String} head - The head of the message
 * @param {Object} body - The data contained in the message
 */
function wsSend(socket, head, body) {
  socket.send(JSON.stringify({
    head: head,
    body: body || ""
  }));
}

/**
 * Handles the reception of WebSocket messages.
 * @param {WebSocket} socket - The WebSocket instance that received the message
 * @param {String} head - The head of the message
 * @param {Object} body - The data contained in the message
 */
function onWsMessageReceived(socket, head, body) {
  switch(head) {
    case "image-base64":
      if(processingPayment)
        return;
      camImg.src = "data:image/jpg;base64," + body;
      break;
    case "labels":
      if(processingPayment)
        return;
      lastLabelsReceived = body;

      // Sort the labels alphabetically to keep the display order static
      lastLabelsReceived.sort((a, b) => {
        return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
      });

      let unknownLabels = [];

      for(let i = 0; i < lastLabelsReceived.length; i++) {
        let l = lastLabelsReceived[i];
        l.displayLabel = capitalizeFirstChar(l.label);
        l.color = labelColors[l.label] || (labelColors[l.label] = randomColor());

        if(!labelInfo[l.label])
          unknownLabels.push(l.label);
      }
      refreshCanvasDisplay();
      updateItemsInfo();

      // Request information on unknown items
      wsSend(socket, "get-items-info", unknownLabels);
      break;
    case "items-info":
      for(let label in body)
        labelInfo[label] = body[label];

      break;
  }
}

/**
 * Attempts to connect to the server.
 * @param {String} location - The server location (IP or URL)
 * @param {function} onMessageReceived - A function that will be called when the socket receives a message
 */
function connectToServer(location, onMessageReceived) {
  let socket = new WebSocket("ws://" + location);

  setConnectionStatus(CONNECTION_STATUS.CONNECTING);
  setTimeout(() => {
    if(CONNECTION_RETRY && CONNECTION_STATUS != CONNECTION_STATUS.OPEN)
      connectToServer(location, onMessageReceived);
    else if(connectionStatus == CONNECTION_STATUS.CONNECTING) {
        setConnectionStatus(CONNECTION_STATUS.CLOSED);
    }
  }, CONNECTION_TIMEOUT);


  socket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    if(onMessageReceived)
      onMessageReceived(socket, data.head, data.body);
  };

  socket.onopen = function(e) {
    setConnectionStatus(CONNECTION_STATUS.OPEN);
    wsSend(socket, "handshake");
  };

  socket.onclose = function(e) {
    if(e.wasClean)
      console.log(`[ws] Connection closed cleanly (code=${e.code} reason=${e.reason})`);
    else if(connectionStatus == CONNECTION_STATUS.OPEN) // e.g. server process killed or network down (event.code is usually 1006 in this case)
      console.log(`[ws] Connection died (code=${e.code} reason=${e.reason})`);
    setConnectionStatus(CONNECTION_STATUS.CLOSED);
  };

  socket.onerror = function(e) {
    if(connectionStatus == CONNECTION_STATUS.OPEN)
      console.log(`[ws] Open WebSocket connection threw an error (code=${e.code} reason=${e.reason})`);
    else {
      console.log(`[ws] Couldn't connect to server at ${location}.`);
      //console.log(`- Retrying in ${(CONNECTION_RETRY_TIME / 1000).toFixed(1)} seconds.`);
    }
    setConnectionStatus(CONNECTION_STATUS.CLOSED);
  };
}

/**
 * Renders the latest image from the camera and the labels and boxes on top
 */
function refreshCanvasDisplay() {
  if(!pictureCanvas)
    return;

  let ctx = pictureCanvas.getContext("2d");
  imgScale = Math.max(pictureCanvas.width / camImg.width, pictureCanvas.height / camImg.height);
  let w = camImg.width * imgScale;

  // Draw a static background color in case there is no image
  ctx.fillStyle = CANVAS_BG_COLOR;
  ctx.fillRect(0, 0, pictureCanvas.width, pictureCanvas.height);

  if(connectionStatus == CONNECTION_STATUS.OPEN) {
    // Draw the image in the background
    ctx.drawImage(camImg, 0, 0, camImg.width * imgScale, camImg.height * imgScale);
    // Draw the labels on top of the image
    redrawLabels();
  }

  // Payment
  if(processingPayment) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
    ctx.fillRect(0, 0, pictureCanvas.width, pictureCanvas.height);
    ctx.font = "30px Arial";
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.fillText("Processing payment", pictureCanvas.width / 2, pictureCanvas.height / 2);
    ctx.font = "22px Arial";
    ctx.fillText("Please wait...", pictureCanvas.width / 2, pictureCanvas.height / 2 + 30);
  }

  // Display information about the connection status
  ctx.textBaseline = "bottom";
  if(connectionStatus == CONNECTION_STATUS.OPEN) {
    ctx.font = "14px Arial";
    ctx.fillStyle = "green";
    ctx.textAlign = "left";
    ctx.fillText("connected", 6, pictureCanvas.height - 6);
  }
  else if(connectionStatus == CONNECTION_STATUS.CONNECTING){
    ctx.font = "30px Arial";
    ctx.fillStyle = "rgb(60, 140, 200)";
    ctx.textAlign = "center";
    ctx.fillText("Connecting...", pictureCanvas.width / 2, pictureCanvas.height / 2);
  }
  else if(connectionStatus == CONNECTION_STATUS.CLOSED) {
    ctx.font = "30px Arial";
    ctx.fillStyle = "red";
    ctx.textAlign = "center";
    ctx.fillText("Disconnected", pictureCanvas.width / 2, pictureCanvas.height / 2);
    ctx.font = "22px Arial";
    ctx.fillText("Refresh the page to attempt to reconnect.", pictureCanvas.width / 2, pictureCanvas.height / 2 + 30);
  }
}

/**
 * Renders the labels and boxes on the canvas
 */
function redrawLabels() {
  let ctx = pictureCanvas.getContext("2d");

  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  for(let i = 0; i < lastLabelsReceived.length; i++) {
    let l = lastLabelsReceived[i];
    let x = l.box[0] * camImg.width * imgScale, y = l.box[1] * camImg.height * imgScale;
    let w = l.box[2] * camImg.width * imgScale, h = l.box[3] * camImg.height * imgScale;

    ctx.strokeStyle = l.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x+w, y);
    ctx.lineTo(x+w,y+h);
    ctx.lineTo(x, y+h);
    ctx.lineTo(x, y);
    ctx.stroke();

    ctx.font = "bold 18px Arial";

    ctx.fillStyle = "rgba(0,0,0,0.3)";
    ctx.fillRect(x + 5, y + 5, ctx.measureText(l.displayLabel).width + 10, 24);

    ctx.fillStyle = l.color;
    ctx.fillText(l.displayLabel, x + 10, y + 22);
  }
}

/**
 * Updates the UI to reflect the items that have been detected
 */
function updateItemsInfo() {
  let list = $("<ul>");

  // Group labels by name and count them
  let items = {};
  for(let i = 0; i < lastLabelsReceived.length; i++) {
    let l = lastLabelsReceived[i];
    if(items[l.label])
      items[l.label].count++;
    else {
      items[l.label] = l;
      items[l.label].count = 1;
    }
  }

  function spaces(n) {
    let str = "";
    for(let i = 0; i < n; i++)
      str += "&nbsp;";
    return str;
  }


  let totalPrice = 0;
  for(let key in items) {
    let it = items[key];
    let li = $("<li>");
    let titleSpan = $("<span>");
    li.append(titleSpan);

    let titleStr = it.displayLabel + (it.count > 1 ? (" (x" + it.count + ")") : "");

    if(labelInfo[key]) {
      let info = labelInfo[key];

      let price = info.price * it.count;
      titleStr += ": " + (Number.isNaN(price) ? info.price : price.toFixed(2) + "€");
      totalPrice += price;

      let infoUl = $("<ul>");

      let isNutritionalData = false;
      if(Number.isNaN(parseFloat(info.energy)))
        infoUl.append($("<li>").text(info.energy + " " + info.proteins + " " + info.carbohydrates + " " + info.fats));
      else if(info.energy + info.proteins + info.carbohydrates + info.fats != 0){
        infoUl.append(
          // # Energy: kcal/100g, Proteins: g/100g, Carbohydrates: g/100g, Fats: g/100g
          $("<li>").html("Energy: " + spaces(13) + "<b>" + info.energy + "</b> <i>kcal/100g</i>"),
          $("<li>").html("Proteins: " + spaces(11) + "<b>" + info.proteins + "</b> <i>g/100g</i>"),
          $("<li>").html("Carbohydrates: " + "<b>" + info.carbohydrates + "</b> <i>g/100g</i>"),
          $("<li>").html("Fats: " + spaces(17) + "<b>" + info.fats + "</b> <i>g/100g</i>")
        );
      }
      li.append(infoUl);
    }
    titleSpan.text(titleStr);
    list.append(li);
  }

  $("#items-info").empty().append(list);
  $("#total-price").text(totalPrice.toFixed(2) + "€");
}

/**
 * Updates the status of the connection to the server and refreshes the display accordingly.
 */
function setConnectionStatus(s) {
  connectionStatus = s;
  if(s == CONNECTION_STATUS.OPEN) {
    $("#button-pay").prop("disabled", false);
  }
  else if(s == CONNECTION_STATUS.CLOSED) {
    $("#button-pay").prop("disabled", true)
  }
  refreshCanvasDisplay();
}

/**
 * Called whenever the user clicks the "pay" button (or, in the future, when the user validates his badge).
 */
function pay() {
  $("#button-pay").prop("disabled", true);
  if(processingPayment)
    return;
  processingPayment = true;
  refreshCanvasDisplay();
  setTimeout(() => {
    $("#button-pay").prop("disabled", false);
    processingPayment = false;
    refreshCanvasDisplay();
  }, PAYMENT_BLOCKING_DURATION);
}

/**
 * Generates a random color.
 * @return {String} a random color in the following format: "rgb(r, g, b)""
 */
function randomColor() {
  function r(min) {return Math.round(min + (255-min) * Math.random());}
  return "rgb(" + [r(120), r(120), r(120)].join(",") + ")";
}

/**
 * Changes the first character of a given string to a capital letter.
 * @param {String} str - The string whose first char will be capitalized
 * @return {String} the given string, with a capital letter at the beginning
 */
function capitalizeFirstChar(str) {
  return str[0].toUpperCase() + str.slice(1);
}
