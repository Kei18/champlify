const { NearScanner } = require('@toio/scanner');
const fs = require('fs');
const http = require('http');

const GRID_FILE = './map/3x4.json';
const NUM_AGNETS = 6;
const INTERVAL_MS = 1000;
const MOVE_SPEED = 80;

const colors = [
  {
    "name": "green",
    "rgb": { red: 0, green: 255, blue: 0 }
  },
  {
    "name": "blue",
    "rgb": { red: 0, green: 0, blue: 255 }
  },
  {
    "name": "red",
    "rgb": { red: 255, green: 0, blue: 0 }
  },
  {
    "name": "orange",
    "rgb": { red: 255, green: 165, blue: 0 }
  },
  {
    "name": "white",
    "rgb": { red: 255, green: 255, blue: 255 }
  },
  {
    "name": "magenta",
    "rgb": { red: 255, green: 0, blue: 255 }
  },
];

const GRID = JSON.parse(fs.readFileSync(GRID_FILE, 'utf8'));

function getPosFromGridToReal(x, y) {
  return {"x": GRID["CELL_SIZE"] * x + GRID["INIT_COORD_X"],
          "y": GRID["CELL_SIZE"] * y + GRID["INIT_COORD_Y"]};
}

function move(cube, x, y) {
  let target = getPosFromGridToReal(x, y);
  cube.moveTo([ target ], {maxSpeed: MOVE_SPEED, moveType: 2});
}

async function main() {
  // connection, "+1" works as smooth connection
  const cubes = await new NearScanner(NUM_AGNETS+1).start();
  for (let i = 0; i < NUM_AGNETS; ++i) {
    let color = colors[i % colors.length];
    console.log(cubes[i].id, i, color["name"]);

    // connect to the cube
    let cube = await cubes[i].connect();

    setInterval(() => {
      cube.turnOnLight(Object.assign({durationMs: 990}, color["rgb"]));
    }, 1000);
  }
  console.log("---\nset toio robots to initial positions\n---");

  const server = http.createServer();
  server.on('request', function(req, res) {
    let filename = req.url;
    const PLAN = JSON.parse(fs.readFileSync(filename));
    for (let t = 0; t < PLAN.length; ++t) {
      for (let i = 0; i < NUM_AGNETS; ++i) {
        setTimeout(() => {
          move(cubes[i], PLAN[t][i]["x"], PLAN[t][i]["y"]);
        }, INTERVAL_MS*t);
      }
    }

    res.writeHead(200,{'Content-Type': 'text/plain'});
    res.write('exec fin\n');
    res.end();
  });
  server.listen(3000);
};

main();
