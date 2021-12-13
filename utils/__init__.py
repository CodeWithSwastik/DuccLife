def new_elo_rating(r1, r2, r1win):

    E1 = 1/(1+10**((r1-r2)/400))
    E2 = 1/(1+10**((r2-r1)/400))
    K = 32
    return r1 + round(K*(r1win-E2)), r2 + round(K*(1-r1win-E1))

def calc_cost(current, starting, base_cost, increase):
    return int(base_cost + (base_cost * ((current-starting)/increase))//2)