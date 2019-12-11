// Network constants
const SERVER_LOCATION = "172.18.0.142:5000";
const CONNECTION_RETRY_TIME = 4000;

// Connection status
const CONNECTION_STATUS = {CLOSED: 0, OPEN: 1};
let connectionStatus = CONNECTION_STATUS.CLOSED;
let connectionAttempts = 0, connectionTimeout = null;

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
let randomLabelPrices = {};

function onWindowResize() {
  if(pictureCanvas) {
    let canvasContainer = $("#picture");
    pictureCanvas.width = canvasContainer.width();
    pictureCanvas.height = canvasContainer.height();
    refreshCanvasDisplay();
  }
}

$(document).ready(() => {
  $("#button-pay").click(pay);

  pictureCanvas = $("#picture canvas")[0];

  onWindowResize();
  window.addEventListener("resize", onWindowResize);
  connectToServer(SERVER_LOCATION, onWsMessageReceived);
});


function wsSend(socket, head, body) {
  socket.send(JSON.stringify({
    head: head,
    body: body || ""
  }));
}

function onWsMessageReceived(head, body) {
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

      for(let i = 0; i < lastLabelsReceived.length; i++) {
        let l = lastLabelsReceived[i];
        l.displayLabel = capitalizeFirstChar(l.label);
        l.color = labelColors[l.label] || (labelColors[l.label] = randomColor());
        l.randomPrice = randomLabelPrices[l.label] || (randomLabelPrices[l.label] = (1 + Math.random() * 3).toFixed(2));
      }
      refreshCanvasDisplay();
      updateItemsInfo();
      break;
  }
}

function connectToServer(location, onMessageReceived) {
  let socket = new WebSocket("ws://" + location);

  connectionAttempts++;
  refreshCanvasDisplay();

  socket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    if(onMessageReceived)
      onMessageReceived(data.head, data.body);
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
    else
      console.log(`[ws] Couldn't connect to server at ${location} - Retrying in ${(CONNECTION_RETRY_TIME / 1000).toFixed(1)} seconds.`);
    setConnectionStatus(CONNECTION_STATUS.CLOSED);
  };

  // Schedule another connection attempt (will only attempt if  this connection fails)
  scheduleConnectionAttempt();
}

function refreshCanvasDisplay() {
  let ctx = pictureCanvas.getContext("2d");
  imgScale = Math.max(pictureCanvas.width / camImg.width, pictureCanvas.height / camImg.height);
  let w = camImg.width * imgScale;

  // Draw a static background color in case there is no image
  ctx.fillStyle = CANVAS_BG_COLOR;
  ctx.fillRect(0, 0, pictureCanvas.width, pictureCanvas.height);
  // Draw the image in the background
  ctx.drawImage(camImg, 0, 0, camImg.width * imgScale, camImg.height * imgScale);
  // Draw the labels on top of the image
  redrawLabels();

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
  else if(connectionStatus == CONNECTION_STATUS.CLOSED){
    ctx.font = "30px Arial";
    ctx.fillStyle = "red";
    ctx.textAlign = "center";
    ctx.fillText("Disconnected", pictureCanvas.width / 2, pictureCanvas.height / 2);
    ctx.font = "22px Arial";
    let attemptsString = connectionAttempts + " attempt" + (connectionAttempts == 1 ? "" : "s");
    ctx.fillText("Trying to reach the server... (" + attemptsString + ")", pictureCanvas.width / 2, pictureCanvas.height / 2 + 30);
  }
}

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

  let totalPrice = 0;
  for(let key in items) {
    let it = items[key];
    let price = it.randomPrice * it.count;
    totalPrice += price;

    let li = $("<li>");
    let infoUl = $("<ul>");
    infoUl.append($("<li>").text("Price : " + price.toFixed(2) + "€"));
    infoUl.append($("<li>").text("Nutritional data:"));
    li.text(it.displayLabel + (it.count > 1 ? (" (x" + it.count + ")") : ""))
    li.append(infoUl);

    list.append(li);
  }

  $("#items-info").empty().append(list);
  $("#total-price").text(totalPrice.toFixed(2) + "€");
}

function scheduleConnectionAttempt() {
  if(connectionTimeout != null)
    return;
  connectionTimeout = setTimeout(() => {
    connectionTimeout = null;
    if(connectionStatus == CONNECTION_STATUS.CLOSED)
      connectToServer(SERVER_LOCATION, onWsMessageReceived);
  }, CONNECTION_RETRY_TIME);
}

function setConnectionStatus(s) {
  connectionStatus = s;
  if(s == CONNECTION_STATUS.OPEN) {
    $("#button-pay").prop("disabled", false);
    connectionAttempts = 0;
    connectionTimeout = null;
  }
  else if(s == CONNECTION_STATUS.CLOSED) {
    $("#button-pay").prop("disabled", true);
    scheduleConnectionAttempt(); // attempt to reconnect after some time
  }
  refreshCanvasDisplay();
}

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

function randomColor() {
  function r(min) {return Math.round(min + (255-min) * Math.random());}
  return "rgb(" + [r(120), r(120), r(120)].join(",") + ")";
}

function capitalizeFirstChar(str) {
  return str[0].toUpperCase() + str.slice(1);
}
