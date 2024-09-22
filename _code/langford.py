def find_pairs(n):
    """
    Finds all Langford pairs for a given integer n.

    A Langford pair is an ordered pair of two permutations of 1, ..., n
    such that they differ by one in each position and the numbers in each permutation are distinct.
    like 234^21^3^1^4

    Args:
        n: The size of the Langford pair to find.

    Returns:
        A list of tuples, where each tuple is a pair of permutations.
    """
    if n < 1:
        return []

    def backtrack(sequence, remaining):
        if len(remaining) == 0:
            return [tuple(sequence)]

        results = []
        for pos in range(2*n):
            if sequence[pos] == 0:
                break
        sorted_num = sorted(remaining)
        for num in sorted_num:
            if pos + num + 1 < 2 * n and sequence[pos + num + 1] == 0:
                sequence[pos] = sequence[pos + num + 1] = num
                remaining.remove(num)
                results.extend(backtrack(sequence, remaining))
                remaining.add(num)
                sequence[pos] = sequence[pos + num + 1] = 0

        return results
    
    def backtrack_link(n):
        def enter(i):
            # step L2
            k = p[0]
            if k == 0:
                result.append(x[:])
                return
            else:
                j = 0
                while x[i] < 0:
                    i += 1
            # step L3 try x[i] = k
            while k > 0:
                if i + k + 1 >= 2*n:
                    return
                elif x[i+k+1] == 0:
                    x[i] = k
                    x[i+k+1] = -k
                    y[i] = j
                    p[j] = p[k]
                    enter(i+1)
                    # step L5 backtrack
                    p[y[i]] = k
                    x[i] = x[i+k+1] = 0
                # step L4 try again
                j = k
                k = p[j]
                    
        # step L1
        x = [0] * (2 * n)
        y = [0] * (2 * n)
        p = [k+1 for k in range(n)]
        p.append(0)
        i = 1
        result = []
        enter(0)
        return result

    sequence = [0] * (2 * n)
    used = [False] * n
    # pairs = backtrack(sequence, set(range(1, n+1)))
    pairs = backtrack_link(n)

    return pairs

# Example usage:
print(find_pairs(7))
