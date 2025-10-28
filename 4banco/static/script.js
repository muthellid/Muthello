// ======================
// Muthello - script
// ======================

const SIZE = 8;

let board1 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
let board2 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
let board3 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
let board4 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
let selectedBoard = board1;

let boardEl = null;
let depthSelect = null;
let whiteScoreEl = null;
let blackScoreEl = null;
let undoBtn = null;
let resetBtn = null;
let colorToggle = null;
let toggleFirstBtn = null;
let styleToggle = null;

let playerColor = 'black';
let aiColor = 'white';
let humanFirst = true;
let grid = [];
let currentTurn = 'black';
let currentBoard = 'board4';
let lastAIMove = null;
let history = [];
let currentStyle = 'normal';

const BOARD_CONFIGS = {
  default: [],
  board1: ['A1','A2','A7','A8','B1','B2','B7','B8','G1','G2','G7','G8','H1','H2','H7','H8'],
  board2: ['B2','G2','B7','G7'],
  board3: ['A1','A2','A7','A8','B1','B8','G1','G8','H1','H2','H7','H8'],
  board4: []
};

function applyStyle(style) {
}
function updateDisplay() {
}

// --- Khởi tạo bàn cờ ---
function initGrid(boardName = currentBoard, style = currentStyle) {
  currentBoard = boardName;
  history = [];

  // ensure boardName fallback
  if (!BOARD_CONFIGS.hasOwnProperty(boardName)) boardName = 'default';

  if (boardName === "board1") {
    selectedBoard = board1 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
    board1[3][3] = "white";
    board1[4][4] = "white";
    board1[3][4] = "black";
    board1[4][3] = "black";
    grid = selectedBoard;
  } else if (boardName === "board2") {
    selectedBoard = board2 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
    board2[3][3] = "white";
    board2[4][4] = "white";
    board2[3][4] = "black";
    board2[4][3] = "black";
    grid = selectedBoard;
  } else if (boardName === "board3") {
    selectedBoard = board3 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
    board3[3][3] = "white";
    board3[4][4] = "white";
    board3[3][4] = "black";
    board3[4][3] = "black";
    grid = selectedBoard;
  } else if (boardName === "board4") {
    selectedBoard = board4 = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
    board4[3][3] = "white";
    board4[4][4] = "white";
    board4[3][4] = "black";
    board4[4][3] = "black";
    grid = selectedBoard;
  } else { // default
    selectedBoard = Array(SIZE).fill().map(() => Array(SIZE).fill(null));
    grid = selectedBoard;
  }

  // style center pieces
  if (style === 'normal') {
    grid[3][3] = 'white'; grid[4][4] = 'white';
    grid[3][4] = 'black'; grid[4][3] = 'black';
  } else {
    grid[3][3] = 'black'; grid[4][4] = 'black';
    grid[3][4] = 'white'; grid[4][3] = 'white';
  }

  // blocked config (safe fallback)
  const blocked = BOARD_CONFIGS[boardName] || [];
  for (let label of blocked) {
    // safe parse: label may be "A10" etc -> use substring
    const row = label.charCodeAt(0) - 65;
    const col = parseInt(label.slice(1), 10) - 1;
    if (row >= 0 && row < SIZE && col >= 0 && col < SIZE) {
      grid[row][col] = 'blocked';
    }
  }

  currentTurn = humanFirst ? playerColor : aiColor;
  lastAIMove = null;

  applyStyle(style);
  updateDisplay();
  renderBoard();
  updateScore();
  highlightMoves();
  if (currentTurn === aiColor) aiPlay();
  renderThumbs();
}

// --- Vẽ bàn cờ ---
function renderBoard() {
  if (!boardEl) return;
  boardEl.innerHTML = '';
  boardEl.style.display = boardEl.style.display || ''; // ensure visible

  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      const cell = document.createElement('div');
      cell.classList.add('cell');
      // add status classes
      const v = grid[y] && grid[y][x];
      if (v === 'black' || v === 'white') cell.classList.add(v);
      if (v === 'blocked') cell.classList.add('blocked');
      cell.onclick = () => handleMove(x, y);
      boardEl.appendChild(cell);
    }
  }
}

// --- Cập nhật điểm ---
function updateScore() {
  if (!whiteScoreEl || !blackScoreEl) return;
  let white = 0, black = 0;
  for (let row of grid) {
    for (let c of row) {
      if (c === 'white') white++;
      if (c === 'black') black++;
    }
  }
  whiteScoreEl.textContent = white;
  blackScoreEl.textContent = black;
}

// --- Tìm nước đi hợp lệ ---
function validMoves(color) {
  const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
  const moves = [];
  if (!grid || !grid.length) return moves;
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      if (grid[y][x] !== null) continue;
      let flips = [];
      for (let [dx, dy] of dirs) {
        let nx = x + dx, ny = y + dy, temp = [];
        while (nx >= 0 && nx < SIZE && ny >= 0 && ny < SIZE) {
          let p = grid[ny][nx];
          if (!p || p === 'blocked') break;
          if (p === color) { if (temp.length) flips.push(...temp); break; }
          temp.push([nx, ny]);
          nx += dx; ny += dy;
        }
      }
      if (flips.length) moves.push({ x, y, flips });
    }
  }
  return moves;
}

// --- Highlight nước đi ---
function highlightMoves() {
  if (!boardEl) return;
  const moves = validMoves(currentTurn);
  const cells = boardEl.children;
  for (let cell of cells) cell.classList.remove('highlight');
  for (let m of moves) {
    const index = m.y * SIZE + m.x;
    if (cells[index]) cells[index].classList.add('highlight');
  }
}

// --- Highlight nước đi AI ---
function highlightLastAIMove(){
  if(!lastAIMove || !boardEl) return;
  const [x, y] = lastAIMove;
  const index = y * SIZE + x;
  const cells = boardEl.children;
  for(let cell of cells) cell.classList.remove('ai-last-move');
  if (cells[index]) cells[index].classList.add('ai-last-move');
}

// --- Áp dụng nước đi ---
function applyMove(x, y, color, flips, isInit=false) {
  if(!grid || !grid.length) return;
  if(!isInit){
    history.push({
      grid: grid.map(r => r.slice()),
      turn: currentTurn,
      lastAIMove: lastAIMove ? [...lastAIMove] : null
    });
  }
  grid[y][x] = color;
  for (let [fx, fy] of flips) {
    if (grid[fy] && typeof grid[fy][fx] !== 'undefined') grid[fy][fx] = color;
  }
  if(!isInit){
    lastAIMove = color === aiColor ? [x, y] : null;
  }
  renderBoard();
  updateScore();
  highlightMoves();
  if(!isInit) highlightLastAIMove();
}

// --- Người chơi click ---
async function handleMove(x, y) {
  if (currentTurn !== playerColor) return;
  const moves = validMoves(playerColor);
  const move = moves.find(m => m.x === x && m.y === y);
  if (!move) return;

  applyMove(x, y, playerColor, move.flips);
  currentTurn = aiColor;
  highlightMoves();

  if (validMoves(aiColor).length > 0) {
    setTimeout(() => aiPlay(), 100);
  } else {
    currentTurn = playerColor;
    highlightMoves();
    if (validMoves(playerColor).length === 0) gameOver();
  }
}

// --- AI đi ---
async function aiPlay() {
  const moves = validMoves(aiColor);
  if (moves.length === 0) {
    currentTurn = playerColor;
    highlightMoves();
    if (validMoves(playerColor).length === 0) gameOver();
    return;
  }

  let depth = 3;
  if (depthSelect && typeof depthSelect.value !== 'undefined') {
    depth = parseInt(depthSelect.value, 10) || depth;
  }

  try {
    const res = await fetch("/ai_move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grid: selectedBoard, depth, aiColor })
    });

    if (!res.ok) { alert("Server lỗi!"); return; }
    const data = await res.json();
    if (data.status === "error") { alert("AI lỗi: "+data.message); return; }

    const move = data.move;
    if (!move) { currentTurn = playerColor; highlightMoves(); return; }

    const m = moves.find(mv => mv.x === move[0] && mv.y === move[1]);
    if (!m) { currentTurn = playerColor; highlightMoves(); return; }

    applyMove(m.x, m.y, aiColor, m.flips);
    currentTurn = playerColor;
    highlightMoves();

    if (validMoves(playerColor).length === 0) {
      currentTurn = aiColor;
      if (validMoves(aiColor).length === 0) gameOver();
      else setTimeout(() => aiPlay(), 100);
    }
  } catch (err) {
    console.error("Kết nối /ai_move lỗi", err);
    alert("Không kết nối server!");
  }
}

// --- Game kết thúc ---
function gameOver() {
  const white = whiteScoreEl ? parseInt(whiteScoreEl.textContent || '0', 10) : 0;
  const black = blackScoreEl ? parseInt(blackScoreEl.textContent || '0', 10) : 0;
  let msg;
  if (white > black) msg = `Trắng thắng ${white} - ${black}`;
  else if (black > white) msg = `Đen thắng ${black} - ${white}`;
  else msg = `Hòa ${white} - ${black}`;
  alert(msg);
}

// --- Setup DOM listeners safely ---
function safeAssign(selectorId, cb) {
  const el = document.getElementById(selectorId);
  if (!el) return null;
  try { cb(el); } catch (e) { console.error("safeAssign error", e); }
  return el;
}

// --- Thumbnail (keeps same behaviour) ---
function renderThumbs() {
  const thumbs = document.querySelectorAll('.thumb');
  thumbs.forEach(t => {
    const boardName = t.dataset.board || 'default';
    const blocked = BOARD_CONFIGS[boardName] || [];
    t.innerHTML = '';
    const size = 20;
    const canvas = document.createElement('canvas');
    canvas.width = size*2; canvas.height = size*2;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#107010';
    ctx.fillRect(0,0,canvas.width,canvas.height);

  // simplified preview
for (let row = 0; row < 2; row++) {
  for (let col = 0; col < 2; col++) {
    const label = String.fromCharCode(65+row) + (col+1);
    if (blocked.includes(label)) {
      ctx.fillStyle = 'rgba(176,48,48,0.7)';
      ctx.fillRect(col*size, row*size, size, size);
    }
  }
}
t.appendChild(canvas);
  });
}
    

// --- Attach listeners and init on DOM ready ---
document.addEventListener("DOMContentLoaded", () => {
  // set DOM refs safely
  boardEl = document.getElementById('board');
  depthSelect = document.getElementById('depthSelect');
  whiteScoreEl = document.getElementById('whiteScore');
  blackScoreEl = document.getElementById('blackScore');

  undoBtn = document.getElementById('undo');
  resetBtn = document.getElementById('reset');
  colorToggle = document.getElementById('colorToggle');
  toggleFirstBtn = document.getElementById('toggleFirst');
  styleToggle = document.getElementById('styleToggle');

  // safe assign handlers only if elements exist
  if (undoBtn) undoBtn.onclick = () => {
    if(history.length === 0) return;
    let steps = Math.min(2, history.length);
    for(let i=0; i<steps; i++){
      const lastState = history.pop();
      grid = lastState.grid.map(r => r.slice());
      currentTurn = lastState.turn;
      lastAIMove = lastState.lastAIMove;
    }
    renderBoard();
    updateScore();
    highlightMoves();
  };

  if (colorToggle) {
    colorToggle.classList.add(playerColor);
    colorToggle.textContent = playerColor === "black" ? "Đen" : "Trắng";
    colorToggle.onclick = () => {
      [playerColor, aiColor] = [aiColor, playerColor];
      colorToggle.className = playerColor;
      colorToggle.textContent = playerColor === "black" ? "Đen" : "Trắng";
      initGrid(currentBoard, currentStyle);
    };
  }

  if (toggleFirstBtn) {
    toggleFirstBtn.onclick = () => {
      humanFirst = !humanFirst;
      toggleFirstBtn.textContent = humanFirst ? "Người đi trước" : "AI đi trước";
      initGrid(currentBoard, currentStyle);
    };
  }

  if (resetBtn) resetBtn.onclick = () => initGrid(currentBoard, currentStyle);
  if (styleToggle) {
    styleToggle.textContent = "Đảo màu";
    styleToggle.onclick = () => {
      currentStyle = currentStyle === 'normal' ? 'reversed' : 'normal';
      initGrid(currentBoard, currentStyle);
    };
  }

  // thumbs click handlers
  document.querySelectorAll('.thumb').forEach(el => {
    el.onclick = () => {
      document.querySelectorAll('.thumb').forEach(t => t.classList.remove('selected'));
      el.classList.add('selected');
      initGrid(el.dataset.board || 'default', currentStyle);
    };
  });

  // finally initialize
  initGrid(currentBoard, currentStyle);
});