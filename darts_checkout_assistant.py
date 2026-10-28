from itertools import product

# Singles are internally represented in the form ('S', value).
# Doubles and trebles are internally represented in the form
# ('D' or 'T', value of the target, single value of the segment).
# A zero placeholder is used to allow for one- and two-dart checkouts.
SINGLES = [('', 0)] + [('S', i) for i in range(1, 21)] + [('S', 25)]
DOUBLES = [('D', 2 * i, i) for i in range(1, 21)] + [('D', 50, 25)]
TREBLES = [('T', 3 * i, i) for i in range(1, 21)]
DARTS = SINGLES + DOUBLES + TREBLES

# LARGEST_DOUBLE and LARGEST_SINGLE don't include 25 or Bull.
# They are handled separately since they are smaller targets (in area)
# than the other singles and doubles, respectively.
LARGEST_DOUBLE = 40
LARGEST_SINGLE = 20
BULL = 50

# These are the finishing doubles in order of preference,
# from highest to lowest.
DOUBLE_PRIORITY = [
    ('D', 32, 16),
    ('D', 16, 8),
    ('D', 40, 20),
    ('D', 24, 12),
    ('D', 8, 4),
    ('D', 36, 18),
    ('D', 28, 14),
    ('D', 20, 10),
    ('D', 12, 6),
    ('D', 4, 2),
    ('D', 38, 19),
    ('D', 34, 17),
    ('D', 30, 15),
    ('D', 26, 13),
    ('D', 22, 11),
    ('D', 18, 9),
    ('D', 14, 7),
    ('D', 10, 5),
    ('D', 6, 3),
    ('D', 2, 1),
    ('D', 50, 25)
    ]

def generate_checkouts(remaining):
    """
    Generate all possible checkouts for the remaining score,
    with the last dart being a double.
    """
    checkouts = [
                 outshot
                 for outshot in product(DARTS, DARTS, DOUBLES)
                 if sum(dart[1] for dart in outshot) == remaining
             ]

    return checkouts

def clean_checkouts(checkouts):
    """
    Remove zero placeholders from the routes
    so that one and two dart checkouts are displayed correctly.
    """
    checkouts = [
                    tuple(dart for dart in option if dart[1] != 0)
                for option in checkouts
                ]

    checkouts = list(dict.fromkeys(checkouts))  # Remove duplicates.
    return checkouts

def filter_checkouts_by_number_of_darts(checkouts):
    """
    Remove all options which use more darts than necessary
    (except for one- and two-dart bull checkouts).
    """
    checkouts_min_darts = []

    for checkout in checkouts:
        if len(checkout) == 1 and checkout[0][1] != BULL:
            checkouts_min_darts.append(checkout)
    if not checkouts_min_darts:
        for checkout in checkouts:
            if len(checkout) == 2 and checkout[1][1] != BULL:
                checkouts_min_darts.append(checkout)
    if not checkouts_min_darts:
        for checkout in checkouts:
            if len(checkout) == 3:
                checkouts_min_darts.append(checkout)

    return checkouts_min_darts

def rank_two_dart_checkouts(checkouts_min_darts, remaining):
    """Decide which route is best for two-dart checkouts."""
    checkouts_single_or_treble = []
    checkouts_before_double_choice = []

    # Prioritise single-to-double checkouts.
    for checkout in checkouts_min_darts:
        if checkout[0] in SINGLES:
            checkouts_before_double_choice.append(checkout)

    # If there are no single-to-double checkouts,
    # retain treble-and bull-first routes.
    if not checkouts_before_double_choice:
        for checkout in checkouts_min_darts:
            if checkout[0] in TREBLES or checkout[0][1] == BULL:
                checkouts_single_or_treble.append(checkout)

    # Prioritise a segment where the single leaves
    # a single-to-double checkout.
    for checkout in checkouts_single_or_treble:
        if (remaining - checkout[0][2] - LARGEST_SINGLE <= LARGEST_DOUBLE
                and checkout[0] in TREBLES):
            checkouts_before_double_choice.append(checkout)

    # Prioritise a segment where the single leaves
    # a 25-to-double checkout.
    if not checkouts_before_double_choice:
        for checkout in checkouts_single_or_treble:
            if (remaining - 25 - LARGEST_SINGLE <= LARGEST_DOUBLE
                    and checkout[0][1] == BULL):
                return checkout

    # Prioritise a segment where the single leaves
    # a single-to-bull checkout.
    if not checkouts_before_double_choice:
        for checkout in checkouts_single_or_treble:
            if (remaining - checkout[0][2] - LARGEST_SINGLE <= BULL
                    and checkout[0] in TREBLES):
                checkouts_before_double_choice.append(checkout)

    # If no checkouts were found in the previous steps,
    # retain all routes.
    if not checkouts_before_double_choice:
        for checkout in checkouts_single_or_treble:
            checkouts_before_double_choice.append(checkout)

    best_checkout = choose_best_double(checkouts_before_double_choice)
    return best_checkout

def rank_three_dart_checkouts(checkouts_min_darts, remaining):
    """Decide which route is best for three-dart checkouts."""
    checkouts_filtered = []
    checkouts_not_ending_on_bull = []
    checkouts_first_dart = []
    checkouts_second_dart = []
    checkouts_d16 = []
    checkouts_favourable_backup = []
    checkouts_before_double_choice = []

    # For 125, aming at the bull is preferred since hitting the bull
    # leaves 75 (25 BULL) and hitting the 25 leaves 100 (T20 D20).
    # This is preferred since having 25 BULL as a backup is better than
    # having treble-to-double as a backup. This property is unique for
    # this number. Therefore, it's treated as a special case.
    if remaining == 125:
        return (('D', 50, 25),('S',25), ('D', 50, 25))

    # Filter out non-sensible checkouts.
    for checkout in checkouts_min_darts:
        if ((checkout[0] in TREBLES or checkout[0][1] == BULL)
                and checkout[1][1] != 25):
            checkouts_filtered.append(checkout)

    # Prioritise checkouts which don't end in bull.
    for checkout in checkouts_filtered:
         if checkout[2][1] != BULL:
             checkouts_not_ending_on_bull.append(checkout)

    # Prioritise going for a treble such that if the single is hit
    # instead, there is still a treble-to-double checkout possibility.
    for checkout in checkouts_not_ending_on_bull:
        has_backup = any(
            remaining - checkout[0][2] - treble[1] == double[1]
                and double[1] != BULL
            for treble in TREBLES
            for double in DOUBLES
        )

        if has_backup and checkout[0][1] != BULL:
            checkouts_first_dart.append(checkout)

    # Prioritise going for a treble such that if the single is hit
    # instead, there is still a treble-to-bull checkout possibility.
    if not checkouts_first_dart:
        for checkout in checkouts_not_ending_on_bull:
            has_backup = any(
                remaining - checkout[0][2] - treble[1] == BULL
                for treble in TREBLES
            )

            if has_backup:
                checkouts_first_dart.append(checkout)

    # If none of the preferred first-dart patterns apply,
    # retain the remaining candidate routes
    if not checkouts_first_dart:
        for checkout in checkouts_not_ending_on_bull:
            checkouts_first_dart.append(checkout)

    # Prioritise the second dart being a single.
    for checkout in checkouts_first_dart:
        if checkout[1] in SINGLES:
            checkouts_second_dart.append(checkout)

    # Prioritise that a single on the second dart leaves bull.
    if not checkouts_second_dart:
        for checkout in checkouts_first_dart:
            if (remaining - checkout[0][1] - checkout[1][2] == BULL
                    and checkout[1] in TREBLES):
                checkouts_second_dart.append(checkout)

    # Prioritise double-double checkouts.
    if not checkouts_second_dart:
        for checkout in checkouts_first_dart:
            if (checkout[1] in DOUBLES and checkout[1] == checkout[2]
                    and checkout[1][1] != BULL):
                checkouts_second_dart.append(checkout)

    # If none of the preferred second-dart patterns apply,
    # retain the remaining candidate routes.
    if not checkouts_second_dart:
        for checkout in checkouts_first_dart:
            checkouts_second_dart.append(checkout)

    # If no checkout finishes on an outer ring double,
    # consider bull finishes.
    if not checkouts_not_ending_on_bull:
        for checkout in checkouts_filtered:
            checkouts_second_dart.append(checkout)

    # Prioritise the finishing double being D16.
    for checkout in checkouts_second_dart:
        if (checkout[2] == ('D', 32, 16) and checkout[0][1] != BULL
                and checkout[1][1] != BULL):
            checkouts_d16.append(checkout)

    # If leaving double 16 isn't possible,
    # retain the remaining candidate routes.
    if not checkouts_d16:
        for checkout in checkouts_second_dart:
            checkouts_d16.append(checkout)

    # Prioritise going for a treble such that if the single is hit
    # instead, a favourable double can still be left by
    # hitting a treble on the second dart.
    for double in DOUBLE_PRIORITY:
        matching_checkouts = []

        for checkout in checkouts_d16:
            has_backup = any(
                remaining - checkout[0][2] - treble[1] == double[1]
                for treble in TREBLES
            )

            if has_backup and checkout[0][1] != BULL:
                matching_checkouts.append(checkout)

        if matching_checkouts:
            checkouts_favourable_backup = matching_checkouts
            break

    # If no backup exists, retain the remaining candidates.
    if not checkouts_favourable_backup:
        for checkout in checkouts_d16:
            checkouts_favourable_backup.append(checkout)

    # Prioritise checkouts where the first two darts
    # are thrown at the same treble.
    for checkout in checkouts_favourable_backup:
        if checkout[0] == checkout[1]:
            checkouts_before_double_choice.append(checkout)

    # Prioritise the first dart being thrown at treble 20.
    if not checkouts_before_double_choice:
        for checkout in checkouts_favourable_backup:
            if checkout[0] == ('T', 60, 20):
                checkouts_before_double_choice.append(checkout)

    # Prioritise the first dart being thrown at treble 19.
    if not checkouts_before_double_choice:
            for checkout in checkouts_favourable_backup:
                if checkout[0] == ('T', 57, 19):
                    checkouts_before_double_choice.append(checkout)

    # Prioritise the first dart being thrown at treble 18.
    if not checkouts_before_double_choice:
            for checkout in checkouts_favourable_backup:
                if checkout[0] == ('T', 54, 18):
                    checkouts_before_double_choice.append(checkout)

    # If none of the preferred patterns apply,
    # retain the remaining candidate routes.
    if not checkouts_before_double_choice:
        for checkout in checkouts_favourable_backup:
            checkouts_before_double_choice.append(checkout)

    best_checkout = choose_best_double(checkouts_before_double_choice)

    return best_checkout

def choose_best_double(checkouts):
    """
    Decide which double to leave according to the priority order.
    Avoid starting on the 25 if possible.
    """
    if not checkouts:
        raise ValueError("At least one checkout is required.")

    for double in DOUBLE_PRIORITY:
        for checkout in checkouts:
            if checkout[0][1] != 25 and checkout[-1] == double:
                return checkout

    return checkouts[0]

def display_checkout(checkout, remaining):
    """
    Convert the selected route into
    a more display-friendly format.
    """
    print(f"The best checkout for {remaining}:")

    formatted = []
    for dart in checkout:
        if dart in  SINGLES:
            formatted.append(f"{dart[1]}")
        elif dart[1] == BULL:
            formatted.append("BULL")
        elif dart in DOUBLES:
            formatted.append(f"D{dart[2]}")
        elif dart in TREBLES:
            formatted.append(f"T{dart[2]}")
    print(' '.join(formatted))

def main():
    """Ask the user for an input and run the applicable functions"""
    try:
        remaining = int(input("Enter the remaining score: "))
    except ValueError:
            print("Please enter a valid integer.")
            return

    if remaining == 0:
            print("You have already won!")
            return
    elif remaining < 0:
            print("A negative score is not possible in darts. " \
                "Please enter a positive score.")
            return
    elif remaining == 1:
            print("If you reach a score of 1, " \
                "you bust and your score will return to what it was " \
                "before your turn. Please enter that score.")
            return
    elif remaining > 170:
            print("The maximum possible checkout is 170. " \
                "Please continue playing until you " \
                "reach a score of 170 or lower, and then enter that score.")
            return

    checkouts = generate_checkouts(remaining)

    checkouts = clean_checkouts(checkouts)

    checkouts = filter_checkouts_by_number_of_darts(checkouts)

    if not checkouts:
        print(f"There are no possible checkouts for {remaining}" \
            "(in darts terminology, this is a bogey number)." \
            "Please continue playing until you reach a score" \
            "that has a possible checkout, and then enter that score.")
        return

    # If there is only one checkout left, no ranking is needed
    # (this is always true for one-dart-checkouts).
    if len(checkouts) == 1:
        display_checkout(checkouts[0], remaining)

    # Check the length of the checkouts.
    # At this stage, every checkout uses the same number of darts.
    elif len(checkouts[0]) == 2:
        checkout = rank_two_dart_checkouts(checkouts, remaining)
        display_checkout(checkout, remaining)

    elif len(checkouts[0]) == 3:
        checkout = rank_three_dart_checkouts(checkouts, remaining)
        display_checkout(checkout, remaining)


if __name__ == "__main__":
    main()