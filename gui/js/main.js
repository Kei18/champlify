const GRID_WIDTH = 5;
const GRID_HEIGHT = 7;
const CELL_SIZE = 100;
const BOARD_WIDTH = 9*CELL_SIZE;
const BOARD_HEIGHT = 9*CELL_SIZE;
const UPDATE_TIME_INTERVAL = 500;

const eel = window["eel"];

const valid_keys = [
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
];

$(function(){

  console.log("start visualization");

  // set window size
  const WINDOW_WIDTH = (window.outerWidth - window.innerWidth) + BOARD_WIDTH;
  const WINDOW_HEIGHT = (window.outerHeight - window.innerHeight) + BOARD_HEIGHT;
  window.resizeTo(WINDOW_WIDTH, WINDOW_HEIGHT);
  window.onresize = function () { window.resizeTo(WINDOW_WIDTH, WINDOW_HEIGHT); };

  function calc_x(x) { return CELL_SIZE*x + CELL_SIZE/2 + CELL_SIZE * 2;}
  function calc_y(y) { return CELL_SIZE*y + CELL_SIZE/2 + CELL_SIZE; }

  let PATHS = [];
  let TYPED_STR = 'a';
  let CHAR_INFO = [ '' ];

  // initiate agents
  $('#agents>circle').each(function(i, elem) {
    const x = $(elem).data('init-x');
    const y = $(elem).data('init-y');
    PATHS.push([x + y * GRID_WIDTH]);
    $(elem).attr('cx', calc_x(x));
    $(elem).attr('cy', calc_y(y));
  });

  // update path
  async function getNewPaths(to_char) {
    const res = await eel.key_pressed(PATHS.map(path => { return path[path.length-1]; }),
                                      to_char, TYPED_STR.length-1)();
    const solution = res["solution"];
    // connectivity check
    if (solution.length <= 1 || solution[0].length != PATHS.length) {
      console.log("solution size is strange");
      return;
    }
    for (let i = 0; i < solution[0].length; ++i) {
      if (solution[0][i] != PATHS[i].slice(-1)) {
        console.log("solution size is strange");
        return;
      }
    }

    // extend paths
    for (let t = 1; t < solution.length; ++t) {
      for (let i = 0; i < solution[t].length; ++i) {
        PATHS[i].push(solution[t][i]);
      }

      // add char info
      if (t == solution.length - 1) {
        CHAR_INFO.push(res['char']);
      } else {
        CHAR_INFO.push('');
      }
    }

    console.log(solution);
  }

  // key pressed
  window.addEventListener("keydown", function(e) {
    if (valid_keys.includes(e.key)) {
      // action
      TYPED_STR += e.key;
      getNewPaths(TYPED_STR.slice(-1));
    }
  });

  // update location
  let current_timestep = 0;
  setInterval(function() {
    // paths are not changed
    if (current_timestep + 1 > PATHS[0].length - 1) return;

    // update timestep
    ++current_timestep;

    // update locations
    for (let i = 0; i < PATHS.length; ++i) {
      const x = PATHS[i][current_timestep] % GRID_WIDTH;
      const y = Math.floor(PATHS[i][current_timestep] / GRID_WIDTH);

      const agent = $('#agent' + i);

      agent.attr('cx', calc_x(x));
      agent.attr('cy', calc_y(y));

      if (CHAR_INFO[current_timestep].length > 0 && CHAR_INFO[current_timestep][y*GRID_WIDTH + x] == '_') {
        agent.addClass('off');
      } else {
        agent.removeClass('off');
      }
    }

    console.log('update locations, timestep=', current_timestep);
  }, UPDATE_TIME_INTERVAL);
});