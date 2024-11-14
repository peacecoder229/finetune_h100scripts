def reverseint(num):
    n_s = str(num)
    revint = list()
    l = len(n_s)
    for i in range(l):
        revint.append(n_s[l -i -1])

    print(str(int("".join(revint))))


reverseint(12345)

