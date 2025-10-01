// I have no idea how to code in JavaScript...

// PRNG implementation {{{ //
class MTwist {
  // Mersenne Twister implementation
  // code copied from: https://github.com/jawj/mtwist
  /**
   * Pass a seed value for reproducible sequences, which are the main reason to
   * use this library over plain Math.random()
   * @param seed An integer between 0 and 4294967295
   */
  constructor(seed = Math.random() * 4294967295) {
    this.mt = new Array(624);
    this.mt[0] = seed >>> 0;
    const n1 = 1812433253;
    for (let mti = 1; mti < 624; mti++) {
      const n2 = this.mt[mti - 1] ^ (this.mt[mti - 1] >>> 30);
      this.mt[mti] = ((((n1 & 0xffff0000) * n2) >>> 0) +
                      (((n1 & 0x0000ffff) * n2) >>> 0) + mti) >>>
                     0;
    }
    this.mti = 624;
  }
  /**
   * Returns an integer in the interval [0,0xffffffff]
   */
  randomUInt32() {
    let y;
    if (this.mti >= 624) {
      for (let i = 0; i < 227; i++) {
        y = ((this.mt[i] & 0x80000000) | (this.mt[i + 1] & 0x7fffffff)) >>> 0;
        this.mt[i] =
            (this.mt[i + 397] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0)) >>> 0;
      }
      for (let i = 227; i < 623; i++) {
        y = ((this.mt[i] & 0x80000000) | (this.mt[i + 1] & 0x7fffffff)) >>> 0;
        this.mt[i] =
            (this.mt[i - 227] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0)) >>> 0;
      }
      y = ((this.mt[623] & 0x80000000) | (this.mt[0] & 0x7fffffff)) >>> 0;
      this.mt[623] =
          (this.mt[396] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0)) >>> 0;
      this.mti = 0;
    }
    y = this.mt[this.mti++];
    y = (y ^ (y >>> 11)) >>> 0;
    y = (y ^ ((y << 7) & 0x9d2c5680)) >>> 0;
    y = (y ^ ((y << 15) & 0xefc60000)) >>> 0;
    y = (y ^ (y >>> 18)) >>> 0;
    return y;
  }
  /**
   * Returns a fractional number in the interval [0,1), just like Math.random
   */
  random() {
    return this.randomUInt32() / 4294967296; // 2^32
  }
  /**
   * Returns an integer in the interval [0,n) with proper uniform distribution
   * [see WARNING](http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/efaq.html)
   * @param maxPlusOne The integer returned will be less than this value
   */
  randomIntBelow(maxPlusOne) {
    if (maxPlusOne < 1)
      throw new Error("Upper bound must be greater than or equal to 1");
    if (maxPlusOne > 4294967296)
      throw new Error("Upper bound must not be greater than 4294967296");
    if (maxPlusOne === 1)
      return 0;
    const bitsNeeded = Math.ceil(Math.log2(maxPlusOne)),
          bitMask = (1 << bitsNeeded) - 1;
    while (true) {
      const int = this.randomUInt32() & bitMask;
      if (int < maxPlusOne)
        return int;
    }
  }
  /**
   * Returns an integer in the interval [m,n] with proper uniform distribution
   * [see WARNING](http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/efaq.html)
   * @param inclusiveMin The integer returned will be no lower than this value
   * @param inclusiveMax The integer returned will be no higher than this value
   */
  randomIntBetween(inclusiveMin, inclusiveMax) {
    return inclusiveMin + this.randomIntBelow(inclusiveMax - inclusiveMin + 1);
  }
  /**
   * Returns true if test calculations match those from the official C code
   */
  static test() {
    const iterationFactor = 10000; // makes max iterations about 400,000
    let seed = 3234567890;
    for (let i = 0; i < 1000; i++) {
      const mtwist = new MTwist(seed),
            iterations = Math.floor(mtwist.randomUInt32() / iterationFactor);
      for (let j = 0; j < iterations; j++)
        mtwist.randomUInt32();
      seed = mtwist.randomUInt32();
    }
    return seed === 1061063157;
  }
}

// }}} PRNG implementation //

async function* create_readline_generator(inputStream) {
  let remainder = '';
  for await (const chunk of inputStream) {
    remainder += chunk;
    let eolIndex;
    while ((eolIndex = remainder.indexOf('\n')) >= 0) {
      // Extract the line up to and including the newline character
      const line = remainder.slice(0, eolIndex);
      remainder = remainder.slice(eolIndex + 1); // Keep the remainder
      yield line;                                // Yield the complete line
    }
  }
}
const stdin_generator = create_readline_generator(process.stdin);

async function read_line() { return (await stdin_generator.next()).value; }

function parse_numbers(line) { return line.split(' ').map((x) => parseInt(x)); }

function parse_map_params(line) {
  const [H, W, num_players] = parse_numbers(line);
  return {height : H, width : W, num_players : num_players};
}

async function read_map() {
  const map_config = parse_map_params(await read_line());
  let track = [];
  for (let i = 0; i < map_config.height; ++i) {
    const row = parse_numbers(await read_line());
    if (row.length != map_config.width) {
      console.error('Warning: row length mismatch (@' + i + ', ' +
                    map_config.width + '!=' + row.length + '}');
    }
    track.push(row);
  }
  return {...map_config, track : track};
}

async function read_observation(map) {
  let line = await read_line();
  if (line == '~~~END~~~') {
    console.error('End of game, exiting.');
    return null;
  }
  const [posx, posy, velx, vely] = parse_numbers(line);
  const agent = {
    x : posx,
    y : posy,
    vel_x : velx,
    vel_y : vely,
  };
  let players = [];
  for (let i = 0; i < map.num_players; ++i) {
    const [pposx, pposy] = parse_numbers(await read_line());
    // Calculating the velocity from the old state is left as an exercise to
    // the reader.
    players.push({
      x : pposx,
      y : pposy,
    });
  }
  return { players: players, agent: agent, }
}

function pos_eq(a, b) { return a.x == b.x && a.y == b.y; }

function traversable(cell_value) { return cell_value >= 0; }

function valid_line(map, pos1, pos2) {
  const track = map.track;
  const height = track.length;
  const width = track[0].length;
  if (pos1.x < 0 || pos1.y < 0 || pos2.x < 0 || pos2.y < 0 ||
      pos1.x >= height || pos1.y >= width || pos2.x >= height ||
      pos2.y >= width) {
    return false;
  }
  const diff = {x : pos2.x - pos1.x, y : pos2.y - pos1.y};
  // Go through the straight line connecting ``pos1`` and ``pos2``
  // cell-by-cell. Wall is blocking if either it is straight in the way or
  // there are two wall cells above/below each other and the line would go
  // "through" them.
  if (diff.x != 0) {
    const slope = diff.y / diff.x;
    const d = Math.sign(diff.x); // direction: left or right
    for (let i = 0, len = Math.abs(diff.x); i <= len; i++) {
      const x = pos1.x + i * d;
      const y = pos1.y + i * slope * d;
      const y_ceil = Math.ceil(y);
      const y_floor = Math.floor(y);
      if (!traversable(track[x][y_ceil]) && !traversable(track[x][y_floor])) {
        return false;
      }
    }
  }
  // Do the same, but examine two-cell-wall configurations when they are
  // side-by-side (east-west).
  if (diff.y != 0) {
    const slope = diff.x / diff.y;
    const d = Math.sign(diff.y); // direction: up or down
    for (let i = 0, len = Math.abs(diff.y); i <= len; i++) {
      const x = pos1.x + i * slope * d;
      const y = pos1.y + i * d;
      const x_ceil = Math.ceil(x);
      const x_floor = Math.floor(x);
      if (!traversable(track[x_ceil][y]) && !traversable(track[x_floor][y])) {
        return false;
      }
    }
  }
  return true;
}

let lc = {
  equalPoints : pos_eq,
  validLine : undefined, // will be initialised after observing stuff
  playerAt : undefined,
};

// Deliberately using the old API
const playerClass = function() {
  var ownData = undefined;
  let rng = new MTwist(1);

  this.init = function(map, playerdata, selfindex) {
    console.error('Bot is initialised');
    // here an initialization might take place;
  };

  this.moveFunction = function(map, playerdata, selfindex) {
    var self = playerdata[selfindex]; // read the info for the actual player
    var newcenter = { // thats how the center of the next movement can be computed
                    x: self.pos.x+(self.pos.x-self.oldpos.x),
                    y: self.pos.y+(self.pos.y-self.oldpos.y)
                };
    var nextmove = newcenter;
    // the variable nextmove is initialized as the center point
    // if it is valid, we stay there with a high probability
    if (!lc.equalPoints(newcenter, self.pos) &&
        lc.validLine(self.pos, newcenter) && lc.playerAt(newcenter) < 0 &&
        rng.random() > 0.1)
      return {
        x : 0,
        y : 0
      };   // with returning 0,0, the next movement will be the center
    else { // the center point is not valid or we want to change with a small
           // probability
      var validmoves = [];
      var validstay = null;
      // we try the possible movements
      for (var i = -1; i <= 1; i++)
        for (var j = -1; j <= 1; j++) {
          nextmove = {x : newcenter.x + i, y : newcenter.y + j};
          // if the movement is valid (the whole line has to be valid)
          if (lc.validLine(self.pos, nextmove) &&
              (lc.playerAt(nextmove) < 0 || lc.playerAt(nextmove) == selfindex))
            if (!lc.equalPoints(nextmove,
                                self.pos)) { // if there is no one else
              validmoves.push(
                  {x : i, y : j}); // we store the movement as a valid movement
            } else {
              validstay = {x : i, y : j}; // the next movement is me
            }
        }
      if (validmoves.length) {
        // if there is a valid movement, try to step there, if it not equal with
        // my actual position
        return validmoves[Math.floor(rng.random() * validmoves.length)];
      } else {
        // if the only one movement is equal to my actual position, we rather
        // stay there
        if (validstay) {
          return validstay;
        }
      }
      return {
        x : 0,
        y : 0
      }; // if there is no valid movement, then close our eyes....
    }
  };
};

function botAdaptor(method, map, observation) {
  let playerdata = [];
  let selfindex = undefined;
  const agent = observation.agent;
  for (let i = 0, len = observation.players.length; i < len; ++i) {
    let cur = {pos : {...observation.players[i]}};
    if (cur.pos.x == agent.x && cur.pos.y == agent.y) {
      cur.oldpos = {
        x : cur.pos.x - agent.vel_x,
        y : cur.pos.y - agent.vel_y,
      };
      selfindex = i;
    }
    playerdata.push(cur);
  }
  const playerAt = function(pos) {
    for (let i = 0, len = observation.players.length; i < len; i++) {
      const cur = observation.players[i];
      if (cur.x == pos.x && cur.y == pos.y) {
        return i;
      }
    }
    return -1;
  };
  lc.playerAt = playerAt;
  lc.validLine = (p1, p2) => valid_line(map, p1, p2);
  return method(map.track, playerdata, selfindex);
}

async function main() {
  console.log('READY')
  const map = await read_map();
  const bot = new playerClass();
  let bot_initialised = false;
  while (true) {
    const observation = await read_observation(map);
    if (observation === null) {
      break;
    }
    if (!bot_initialised) {
      botAdaptor(bot.init, map, observation);
      bot_initialised = true;
    }
    const delta = botAdaptor(bot.moveFunction, map, observation);
    console.log(delta.x + ' ' + delta.y)
  }
}

await main();
stdin_generator.return()

/* vim:set et sw=2 ts=2 fdm=marker: */
