const express = require("express");
const os = require("os");

const app = express();
const PORT = 3000;

app.get("/", (req, res) => {
  res.send(`Hello from container 👋
Hostname: ${os.hostname()}
User ID: ${process.getuid()}`);
});

app.get("/health", (req, res) => {
  res.status(200).send("OK");
});

app.listen(PORT, () => {
  console.log(`App running on port ${PORT}`);
});
