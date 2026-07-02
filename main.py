import flet as ft
import random
import math


# ============================================================
# AI ロジック
# ============================================================

def calculate_winner(squares):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]
    for a, b, c in lines:
        if squares[a] and squares[a] == squares[b] == squares[c]:
            return squares[a]
    return None


def is_board_full(squares):
    return all(s != "" for s in squares)


def get_empty_indices(squares):
    return [i for i, s in enumerate(squares) if s == ""]


def minimax(squares, is_maximizing):
    winner = calculate_winner(squares)
    if winner == "O":
        return 1
    if winner == "X":
        return -1
    if is_board_full(squares):
        return 0
    if is_maximizing:
        best = -math.inf
        for i in get_empty_indices(squares):
            squares[i] = "O"
            score = minimax(squares, False)
            squares[i] = ""
            best = max(best, score)
        return best
    else:
        best = math.inf
        for i in get_empty_indices(squares):
            squares[i] = "X"
            score = minimax(squares, True)
            squares[i] = ""
            best = min(best, score)
        return best


def ai_move_hard(squares):
    best_score = -math.inf
    best_move = -1
    for i in get_empty_indices(squares):
        squares[i] = "O"
        score = minimax(squares, False)
        squares[i] = ""
        if score > best_score:
            best_score = score
            best_move = i
    return best_move


def ai_move_normal(squares):
    if random.random() < 0.7:
        return ai_move_hard(squares)
    return random.choice(get_empty_indices(squares))


def ai_move_easy(squares):
    return random.choice(get_empty_indices(squares))


def ai_move_lose(squares):
    empty = get_empty_indices(squares)
    if len(empty) == 1:
        return empty[0]
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]
    no_win_moves = []
    for i in empty:
        squares[i] = "O"
        if calculate_winner(squares) != "O":
            no_win_moves.append(i)
        squares[i] = ""
    if not no_win_moves:
        return empty[0]

    def creates_o_threat(idx):
        squares[idx] = "O"
        for a, b, c in lines:
            vals = [squares[a], squares[b], squares[c]]
            if vals.count("O") == 2 and vals.count("") == 1:
                squares[idx] = ""
                return True
        squares[idx] = ""
        return False

    safe = [i for i in no_win_moves if not creates_o_threat(i)]
    return random.choice(safe) if safe else random.choice(no_win_moves)


def get_ai_move(squares, difficulty):
    if difficulty == "hard":
        return ai_move_hard(squares)
    elif difficulty == "normal":
        return ai_move_normal(squares)
    elif difficulty == "lose":
        return ai_move_lose(squares)
    return ai_move_easy(squares)


def is_draw_likely(squares):
    empty = get_empty_indices(squares)
    if len(empty) > 3:
        return False
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]
    for a, b, c in lines:
        vals = [squares[a], squares[b], squares[c]]
        if "X" not in vals and vals.count("O") >= 1:
            return False
    return True


GAG_COMMENTS = [
    "ここ空いてない...？",
    "えっ、ダメ？",
    "盤面せまいよ〜",
    "ルールよくわかんない",
    "こっちの方が良くない？",
    "はみ出しちゃった☆",
    "枠とは...？",
    "自由に生きたい",
]

STRAY_POSITIONS = [
    (-70, 20), (210, -30), (-60, 100), (220, 80),
    (-50, 170), (210, 150), (80, -30), (80, 210),
]


# ============================================================
# UI（命令的スタイル）
# ============================================================

def main(page: ft.Page):
    page.title = "Tic Tac Toe"
    page.padding = 20

    # --- ゲーム状態 ---
    squares = [""] * 9
    vs_cpu = True
    difficulty = "normal"
    score_x = 0
    score_o = 0
    score_draw = 0
    stray_count = 0
    game_over = False

    # --- UI部品 ---
    buttons = []
    for i in range(9):
        btn = ft.ElevatedButton(
            content=ft.Text(""),
            width=70,
            height=70,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), padding=0),
            on_click=lambda e, idx=i: on_square_click(idx),
        )
        buttons.append(btn)

    status_text = ft.Text("Your turn (X)", size=18, weight=ft.FontWeight.BOLD)
    score_text = ft.Text("", size=14)
    mode_text = ft.Text("", size=14)
    new_game_btn = ft.ElevatedButton("🔄 New Game", visible=False, on_click=lambda _: new_game())
    reset_btn = ft.OutlinedButton("🗑️ Reset Scores", visible=False, on_click=lambda _: reset_scores())
    menu_btn = ft.TextButton("🏠 Menu", on_click=lambda _: show_menu())

    # 盤面外のO表示用コンテナ
    stray_container = ft.Stack(width=400, height=300)

    board_row1 = ft.Row([buttons[0], buttons[1], buttons[2]], spacing=4)
    board_row2 = ft.Row([buttons[3], buttons[4], buttons[5]], spacing=4)
    board_row3 = ft.Row([buttons[6], buttons[7], buttons[8]], spacing=4)
    board_grid = ft.Column([board_row1, board_row2, board_row3], spacing=4)

    game_view = ft.Column(
        [
            ft.Row([mode_text, menu_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=5),
            score_text,
            ft.Divider(height=5),
            status_text,
            ft.Row([
                ft.Stack(
                    [
                        ft.Container(board_grid, left=80, top=40),
                        stray_container,
                    ],
                    width=400,
                    height=300,
                )
            ]),
            ft.Row([new_game_btn, reset_btn], spacing=10),
        ],
        spacing=8,
    )

    # メニュー画面
    menu_view = ft.Column(
        [
            ft.Text("🎮 Tic Tac Toe", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            ft.Text("1P vs CPU", size=16, weight=ft.FontWeight.W_600),
            ft.Row([
                ft.ElevatedButton("Easy 🟢", on_click=lambda _: start_game(True, "easy"),
                                  style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_100)),
                ft.ElevatedButton("Normal 🟡", on_click=lambda _: start_game(True, "normal"),
                                  style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_100)),
                ft.ElevatedButton("Hard 🔴", on_click=lambda _: start_game(True, "hard"),
                                  style=ft.ButtonStyle(bgcolor=ft.Colors.RED_100)),
            ]),
            ft.Divider(height=10),
            ft.ElevatedButton("接待モード 🎁 (絶対勝てる)", width=250, on_click=lambda _: start_game(True, "lose"),
                              style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_100)),
            ft.Divider(height=20),
            ft.ElevatedButton("2P 対戦 👥", width=200, on_click=lambda _: start_game(False, "")),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # --- ロジック ---
    def update_board():
        nonlocal game_over
        for i in range(9):
            val = squares[i]
            if val == "X":
                buttons[i].content = ft.Icon(ft.Icons.CLOSE)
            elif val == "O":
                buttons[i].content = ft.Icon(ft.Icons.CIRCLE_OUTLINED)
            else:
                buttons[i].content = ft.Text("")

        winner = calculate_winner(squares)
        if winner:
            status_text.value = f"🎉 Winner: {winner}"
            game_over = True
        elif is_board_full(squares):
            status_text.value = "🤝 Draw!"
            game_over = True
        else:
            if vs_cpu:
                status_text.value = "Your turn (X)"
            else:
                x_n = squares.count("X")
                o_n = squares.count("O")
                status_text.value = f"Next player: {'X' if x_n <= o_n else 'O'}"

        score_text.value = f"❌ X: {score_x}   🤝 Draw: {score_draw}   ⭕ O: {score_o}"
        new_game_btn.visible = game_over
        reset_btn.visible = game_over

        # stray表示 - めちゃくちゃな位置に散らばる
        stray_container.controls.clear()
        random.seed(42)  # 位置を固定して毎回同じ場所に出す
        for idx in range(stray_count):
            comment = GAG_COMMENTS[idx % len(GAG_COMMENTS)]
            # めちゃくちゃな位置
            x = random.randint(-80, 350)
            y = random.randint(-50, 280)
            angle = random.uniform(-0.5, 0.5)
            size = random.randint(18, 40)
            stray_container.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.CIRCLE_OUTLINED, size=size),
                        ft.Text(comment, size=9, italic=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    left=x,
                    top=y,
                    rotate=ft.Rotate(angle),
                )
            )
        random.seed()  # シードをリセット

        page.update()

    def on_square_click(i):
        nonlocal game_over, score_x, score_o, score_draw, stray_count
        if squares[i] or game_over:
            return

        if vs_cpu:
            squares[i] = "X"

            if not calculate_winner(squares) and not is_board_full(squares):
                if difficulty == "lose" and is_draw_likely(squares):
                    stray_count += 1
                else:
                    cpu_i = get_ai_move(squares, difficulty)
                    squares[cpu_i] = "O"
        else:
            x_n = squares.count("X")
            o_n = squares.count("O")
            squares[i] = "X" if x_n <= o_n else "O"

        # スコア
        w = calculate_winner(squares)
        if w == "X":
            score_x += 1
        elif w == "O":
            score_o += 1
        elif is_board_full(squares):
            score_draw += 1

        update_board()

    def new_game():
        nonlocal squares, game_over, stray_count
        squares = [""] * 9
        game_over = False
        stray_count = 0
        update_board()

    def reset_scores():
        nonlocal score_x, score_o, score_draw
        score_x = 0
        score_o = 0
        score_draw = 0
        new_game()

    def start_game(cpu, diff):
        nonlocal vs_cpu, difficulty, score_x, score_o, score_draw
        vs_cpu = cpu
        difficulty = diff
        score_x = 0
        score_o = 0
        score_draw = 0
        mode_text.value = (
            "🎮 接待モード 🎁" if diff == "lose"
            else f"🎮 vs CPU ({diff.capitalize()})" if cpu
            else "🎮 2P対戦"
        )
        new_game()
        page.controls.clear()
        page.add(ft.SafeArea(content=game_view))
        page.update()

    def show_menu():
        page.controls.clear()
        page.add(ft.SafeArea(content=menu_view))
        page.update()

    # 起動時: メニュー表示
    show_menu()


if __name__ == "__main__":
    ft.app(target=main)
