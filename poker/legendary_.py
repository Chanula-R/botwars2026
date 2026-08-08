def nextMove(gameState):
    call, pot, stack = gameState.amount_to_call, gameState.pot, gameState.your_stack
    r1, r2 = gameState.your_hole_cards[0][1], gameState.your_hole_cards[1][1]
    hi, lo = max(r1, r2), min(r1, r2)
    is_pair = r1 == r2
    suited = gameState.your_hole_cards[0][0] == gameState.your_hole_cards[1][0]
    pot_odds = call / (pot + call) if call else 0

    def bet_size(frac, floor_frac):
        return min(stack, max(int(pot * frac), int(stack * floor_frac), 1))

    if gameState.street == "preflop":
        pts = {14: 10, 13: 8, 12: 7, 11: 6, 10: 5}.get(hi, hi / 2)
        if is_pair:
            pts = max(pts * 2, 5)
        else:
            pts += 2 if suited else 0
            gap = hi - lo - 1
            pts -= {0: 0, 1: 1, 2: 2, 3: 4}.get(gap, 5)
            pts += 1 if gap <= 1 and hi < 12 else 0

        premium = pts >= 9
        playable = pts >= 5

        if not playable:
            return ("check",) if call == 0 else ("fold",)
        if call == 0:
            return ("bet", bet_size(1, 0.05 if premium else 0.025))
        if premium and gameState.min_raise_to:
            return ("raise", min(stack, max(gameState.min_raise_to, bet_size(1, 0.08))))
        return ("call",) if premium or pot_odds <= 0.25 else ("fold",)

    all_cards = gameState.your_hole_cards + gameState.community_cards
    ranks = [c[1] for c in all_cards]
    suits = [c[0] for c in all_cards]
    board_ranks = [c[1] for c in gameState.community_cards]
    counts = sorted((ranks.count(r) for r in set(ranks)), reverse=True)
    suit_counts = {s: suits.count(s) for s in set(suits)}

    has_flush = any(n >= 5 for n in suit_counts.values())
    flush_draw = not has_flush and any(n == 4 for n in suit_counts.values())
    u = set(ranks) | ({1} if 14 in ranks else set())
    windows = [set(range(s, s + 5)) for s in range(1, 11)]
    has_straight = any(w <= u for w in windows)
    straight_draw = not has_straight and any(len(w & u) == 4 for w in windows)

    is_quads = counts[0] == 4
    is_full_house = counts[0] == 3 and len(counts) > 1 and counts[1] >= 2
    is_trips = counts[0] == 3
    is_two_pair = counts[0] == 2 and len(counts) > 1 and counts[1] == 2
    top_board = max(board_ranks)
    top_pair = r1 == top_board or r2 == top_board
    overpair = is_pair and r1 > top_board
    matches_board = r1 in board_ranks or r2 in board_ranks

    monster = has_straight or has_flush or is_full_house or is_quads or is_trips
    strong = is_two_pair or overpair or top_pair
    live_draw = (flush_draw or straight_draw) and gameState.street != "river"
    weak_pair = (is_pair or matches_board) and not strong

    if monster:
        if call == 0:
            return ("bet", bet_size(0.8, 0.08))
        if gameState.min_raise_to:
            size = stack if pot_odds < 0.4 else bet_size(1, 0.1)
            return ("raise", min(stack, max(size, gameState.min_raise_to)))
        return ("call",)

    if strong:
        if call == 0:
            return ("bet", bet_size(0.65, 0.05))
        return ("call",) if pot_odds <= 0.4 else ("fold",)

    if live_draw or weak_pair:
        if call == 0:
            return ("bet", bet_size(0.4, 0.025))
        return ("call",) if pot_odds <= 0.22 else ("fold",)

    if call == 0:
        scary = len(set(board_ranks)) == len(board_ranks) and top_board >= 12
        if scary and stack > pot * 3:
            return ("bet", bet_size(0.5, 0.03))
        return ("check",)
    return ("fold",)
