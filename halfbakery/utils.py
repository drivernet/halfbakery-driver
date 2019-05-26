def raw_votes_parse(raw_votes):

    votes = raw_votes.replace('(', '').replace(')', '')

    if ',' in votes:
        pos, neg = votes.split(', ')
        pos = int(pos.replace('+', ''))
        neg = int(neg.replace('-', ''))
    else:
        if votes.startswith('+'):
            pos, neg = int(votes[1:]), 0
        elif votes.startswith('-'):
            pos, neg = 0, int(votes[1:])
        else:
            pos, neg = 0, 0

    return {'positive': pos, 'negative': neg}


def meal_votes_parse(meal_votes):

    meal, raw_votes = meal_votes.split(': ')
    meal = float(meal)
    votes = raw_votes_parse(raw_votes)

    return {'meal': meal,
            'votes': votes}
