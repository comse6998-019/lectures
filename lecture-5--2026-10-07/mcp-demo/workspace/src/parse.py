def total(xs, n):
    s, i = 0, 0
    while i <= n:
        s += xs[i]
        i = i + 1
    return s
