document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM loaded");

    // Инициализация шахматной доски
    var board = Chessboard('chessboard', {
        draggable: true, // Разрешить перетаскивание фигур
        position: 'start', // Начальная позиция
        onDrop: handleMove, // Обработчик хода
    });

    // Инициализация игры
    var game = new Chess();

    // Функция обработки хода
    function handleMove(source, target) {
        // Пытаемся сделать ход
        const move = game.move({
            from: source,
            to: target,
            promotion: 'q', // Автоматическое превращение пешки в ферзя
        });

        // Если ход недопустимый, возвращаем фигуру на место
        if (move === null) {
            return 'snapback';
        }

        // Обновляем доску
        updateBoard();

        // Проверяем, закончилась ли игра
        if (game.isGameOver()) {
            if (game.isCheckmate()) {
                alert("Шах и мат! Игра окончена.");
            } else if (game.isDraw()) {
                alert("Ничья! Игра окончена.");
            }
        }
    }

    // Функция обновления доски
    function updateBoard() {
        board.position(game.fen()); // Обновляем позицию на доске
    }

    // Кнопка для сброса игры
    document.getElementById('reset-game').addEventListener('click', function () {
        game.reset(); // Сбрасываем игру
        board.start(); // Сбрасываем доску
    });

    // Кнопка для отмены хода
    document.getElementById('undo-move').addEventListener('click', function () {
        game.undo(); // Отменяем последний ход
        updateBoard(); // Обновляем доску
    });
});