var board_cfg = {
  position: '{{ fen }}',
  showNotation: true,
  draggable: true,
  onDragStart: onDragStart,
  onDrop: onDrop
};
var board = ChessBoard('board', board_cfg);
var current_turn = 'w';
var game_id = -1;

setInterval(function() {
  $.get('game/update_data', function(data) {
      board.position(data.fen);
      current_turn = data.current_turn;
  });
}, 3000); // 3 seconds

function onDrop(source, target, piece, orientation) {
  console.log("Try move: " + piece + " from " + source + " to " + target);
  
  const params = {
    piece: piece,
    source: source,
    target: target
  };

  $.get('/game/move', params, function(data) {
    console.log("Move response: " + data.message);
    board.position(data.fen);
    current_turn = data.current_turn; 
  });
}

function onDragStart(source, piece, position, orientation) {
  if (
    (current_turn === 'w' && piece.search(/^w/) === -1) ||
    (current_turn === 'b' && piece.search(/^b/) === -1)
  ) {
    return false;
  }
}

$('#reset').click(function() {
  $.get('/reset', function(data) {
    board.position(data.fen);
    document.querySelector('#pgn').innerText = data.pgn;
  });
});

$('#undo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/undo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});

$('#redo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/redo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});
