var board_cfg = {
  position: '{{ fen }}',
  showNotation: true,
  draggable: true,
  onDragStart: onDragStart,
  onDrop: onDrop
};
var board = ChessBoard('board', board_cfg);
var turn_color = 'white';
var game_id = -1;

setInterval(function() {
  $.get('game/update_data', function(data) {
      board.position(data.fen);
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
    turn_color = data.turn_color; 
  });
}

function onDragStart(source, piece, position, orientation) {
  if (
    (turn_color === 'white' && piece.search(/^w/) === -1) ||
    (turn_color === 'black' && piece.search(/^b/) === -1)
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
