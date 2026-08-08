def nextMove(g):
    h,b = g.your_hole_cards,g.community_cards
    call,pot,stack = max(0,g.amount_to_call),max(0,g.pot),max(0,g.your_stack)
    r1,r2 = h[0][1],h[1][1]

    if g.street == "preflop":
        hi,lo=max(r1,r2),min(r1,r2)
        gap=hi-lo
        s=hi*3+lo

        if r1==r2: s+=28+hi*2
        if h[0][0]==h[1][0]: s+=6
        if gap==1: s+=8
        elif gap==2: s+=4
        elif gap>=5: s-=5
        if hi==14 and lo>=10: s+=12
        elif hi>=12 and lo>=10: s+=7

        if call==0:
            if s>=85: return bet(g,pot,stack,.55)
            if s>=68: return bet(g,pot,stack,.38)
            if s>=56: return bet(g,pot,stack,.25)
            return ("check",)

        odds=call/max(1,pot+call)
        if s>=88 or (s>=72 and odds<=.42) or (s>=60 and odds<=.27):
            return ("call",)
        return ("fold",)

    cards=h+b
    cat=category(cards)
    br=[x[1] for x in b]
    top=max(br)

    overpair=r1==r2 and r1>top
    top_pair=(r1==top or r2==top) and max(r1,r2)>=11

    suits={}
    ranks=set()

    for s,r in cards:
        suits[s]=suits.get(s,0)+1
        ranks.add(r)

    flush_draw=len(b)<5 and 4 in suits.values()
    straight_draw=len(b)<5 and draw(ranks)
    strong_draw=flush_draw or straight_draw

    if call==0:
        if cat>=6: return bet(g,pot,stack,.80)
        if cat>=4: return bet(g,pot,stack,.65)
        if cat>=2: return bet(g,pot,stack,.50)
        if overpair or top_pair: return bet(g,pot,stack,.38)
        if strong_draw: return bet(g,pot,stack,.30)
        return ("check",)

    odds=call/max(1,pot+call)

    if cat>=4: return ("call",)
    if cat>=3 and odds<=.50: return ("call",)
    if cat==2 and odds<=.40: return ("call",)
    if overpair and odds<=.35: return ("call",)
    if top_pair and odds<=.29: return ("call",)
    if strong_draw and odds<=.26: return ("call",)
    return ("fold",)


def category(cards):
    counts,suits={},{}
    for s,r in cards:
        counts[r]=counts.get(r,0)+1
        suits.setdefault(s,[]).append(r)

    if any(len(x)>=5 and straight(x) for x in suits.values()): return 8

    v=list(counts.values())
    if 4 in v: return 7

    trips=sum(x>=3 for x in v)
    pairs=sum(x>=2 for x in v)

    if trips>=2 or (trips and pairs>=2): return 6
    if any(len(x)>=5 for x in suits.values()): return 5
    if straight(counts): return 4
    if trips: return 3
    if pairs>=2: return 2
    return 1 if pairs else 0


def straight(ranks):
    r=set(ranks)
    if 14 in r: r.add(1)
    return any(all(x in r for x in range(i,i+5)) for i in range(1,11))


def draw(ranks):
    r=set(ranks)
    if 14 in r: r.add(1)
    return any(len(r & set(range(i,i+5)))==4 for i in range(1,11))


def bet(g,pot,stack,f):
    if stack<=0: return ("check",)

    lo=max(1,getattr(g,"min_bet",1))
    hi=min(stack,getattr(g,"max_bet",stack))
    amount=pot*f if pot else stack*.05

    return ("bet",int(max(lo,min(amount,hi))))
