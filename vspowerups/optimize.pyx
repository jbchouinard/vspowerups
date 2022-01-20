from collections import Counter

from libc.stdint cimport uintptr_t


cdef struct Powerup:
    int cost
    int tier


cdef int strictly_smaller(Powerup p1, Powerup p2):
    if p1.cost > p2.cost:
        return 0
    elif p1.tier > p2.tier:
        return 0
    elif p1.cost < p2.cost:
        return 1
    elif p1.tier < p2.tier:
        return 1
    else:
        return 0


def c_permutations(uintptr_t pvals, uintptr_t pcounts, int size):
    cdef Powerup[14] vals = <Powerup*> pvals
    cdef int[14] counts = <int*> pcounts
    cdef int i
    cdef int j
    cdef int n
    if size == 0:
        yield []
        return
    for i in range(14):
        if counts[i] > 0:
            n = i
    n += 1
    if size == 1:
        for i in range(n):
            if counts[i] > 0:
                yield [vals[i]]
    elif n == 1:
        yield [vals[0]] * size
    else:
        for i in range(n):
            if counts[i] == 0:
                continue
            counts[i] -= 1
            for j in range(n):
                if (
                    i != j and
                    counts[j] and
                    strictly_smaller(vals[i], vals[j])
                ):
                    break
            else:  # no break
                for rest in c_permutations(<uintptr_t> vals, <uintptr_t> counts, size - 1):
                    if rest:
                        yield [vals[i]] + rest
            counts[i] += 1


def permutations(counts, int size):
    cdef int i
    cdef Powerup[14] c_vals
    cdef int[14] c_counts
    cdef uintptr_t cp_vals = <uintptr_t> c_vals
    cdef uintptr_t cp_counts = <uintptr_t> c_counts

    for i in range(14):
        c_counts[i] = 0

    for i, (val, count) in enumerate(counts):
        c_vals[i] = Powerup(val[0], val[1])
        c_counts[i] = count

    for order in c_permutations(cp_vals, cp_counts, size):
        yield [(v["cost"], v["tier"]) for v in order]


cpdef int full_upgrade_cost(int base_cost, int tiers, int n_upgrades):
    cdef int cost = base_cost / 10
    cdef int n = 10 + n_upgrades
    if tiers == 0:
        return 0
    elif tiers == 1:
        return n * cost
    elif tiers == 2:
        return (3 * n + 2) * cost
    elif tiers == 3:
        return (6 * n + 8) * cost
    elif tiers == 4:
        return (10 * n + 20) * cost
    else:
        return (15 * n + 40) * cost


def total_cost(pwtypes, int size):
    cdef int n_upgrades = 0
    cdef int total_cost = 0
    cdef int i
    cdef int base_cost
    cdef int tiers
    for i in range(size):
        base_cost = pwtypes[i][0]
        tiers = pwtypes[i][1]
        total_cost += full_upgrade_cost(base_cost, tiers, n_upgrades)
        n_upgrades += tiers

    return total_cost


def optimize_cost(pwtypes):
    cdef int size = len(pwtypes)
    cdef int cost
    cdef int best_cost = 1000000
    counts = [list(x) for x in list(Counter(pwtypes).items())]
    best_order = []
    for order in permutations(counts, size):
        cost = total_cost(order, size)
        if cost < best_cost:
            best_cost = cost
            best_order = order

    return best_cost, best_order
