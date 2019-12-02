let socket = new WebSocket("ws://172.18.0.6:5000");

let canvas = document.getElementById("test");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
let ctx = canvas.getContext("2d");

function wsSend(head, body) {
  let obj = {
    head: head,
    body: body || ""
  };
  socket.send(JSON.stringify(obj));
}

let camImg = new Image();
camImg.onload = function() {
  imgScale = Math.max(canvas.width / camImg.width, canvas.height / camImg.height);
  let w = camImg.width * imgScale;
  ctx.drawImage(camImg, 0, 0, camImg.width * imgScale, camImg.height * imgScale); // Or at whatever offset you like
  redrawLabels();
};

let imgScale = 0;
let lastLabelsReceived = [];

socket.onmessage = function(e) {
  let data = JSON.parse(e.data);
  let head = data.head, body = data.body;

  console.log("[FRONT < MAIN] " + head)

  switch(head) {
    case "image-base64":
      camImg.src = "data:image/jpg;base64," + body;
      break;
    case "labels":
      if(camImg == null)
        return;
        lastLabelsReceived = body;
        redrawLabels();
      break;
  }
};

socket.onopen = function(e) {
  console.log("Connection established")
  wsSend("handshake");
};

socket.onclose = function(e) {
  if(e.wasClean)
    console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
  else {
    // e.g. server process killed or network down (event.code is usually 1006 in this case)
    console.log("Connection died");
  }
};

socket.onerror = function(error) {
  console.error(JSON.stringify(error))
  alert(`[ERROR] ${error}`);
};

function redrawLabels() {
  for(let i = 0; i < lastLabelsReceived.length; i++) {
    let l = lastLabelsReceived[i];
    console.log(l.box)
    let x = l.box[0] * camImg.width * imgScale, y = l.box[1] * camImg.height * imgScale;
    let w = l.box[2] * camImg.width * imgScale, h = l.box[3] * camImg.height * imgScale;

    ctx.strokeStyle = "red";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x+w, y);
    ctx.lineTo(x+w,y+h);
    ctx.lineTo(x, y+h);
    ctx.lineTo(x, y);
    ctx.stroke();

    ctx.fillStyle = "red";
    ctx.font = "14px Arial";
    ctx.fillText(l.label, x + 10, y + 20);
  }
}
