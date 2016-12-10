from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_http_methods


from collections import Counter
from itertools import cycle
import random

from .models import Card, Game, Word, Clue, Guess, Comment, TURN_STATES
from django.contrib.auth.models import User


def augment_context(request):
    return {'request_user': request.user}


def index(request):
    return render(request, 'codenames/index.html')


def about(request):
    return render(request, 'codenames/about.html')


def waiting(request, user_id):
    '''Sends a JsonResponse back with 'true'
    if there are games waiting on this user'''
    if not user_id or user_id == 'None':
        return JsonResponse({'waitingOnYou': False})
    user = User.objects.filter(id=user_id).first()

    giving, guessing = find_games(user)
    waiting_on_you = find_waiting_games(user, giving, guessing)
    return JsonResponse({'waitingOnYou': waiting_on_you != []})


def game(request, unique_id):
    try:
        current_game = get_object_or_404(Game, unique_id=unique_id)
    except (KeyError, Game.DoesNotExist):
        return render(request, 'codenames/game.html', {
            'error_message': "This game doesn't exist.",
        })

    cards = current_game.card_set.order_by('pk')

    word_context = [{'id': card.word.id, 'text': card.word.text, 'color': card.color, 'chosen': card.chosen}
                    for card in cards]
    word_rows = [word_context[i:i + 5] for i in range(0, 25, 5)]
    clues = list(current_game.clue_set.order_by('id'))
    try:
        current_clue = clues[-1]
    except IndexError:
        current_clue = ''

    context = {
        'word_rows': word_rows,
        'active': current_game.active,
        'current_turn': current_game.get_current_turn_display,
        'team_color': current_game.current_turn,
        'past_clues': clues,
        'current_clue': current_clue,
        'current_guess_number': current_game.current_guess_number,
        'past_guesses': current_game.guess_set.order_by('id'),
        'current_player': current_game.current_player(),
        'user_is_giver': current_game.is_giver(request.user),
        'players': {
            'Red Team': current_game.red_team(),
            'Blue Team': current_game.blue_team()
        },
        'comments': current_game.comment_set.all()
    }
    return render(request, 'codenames/game.html', context)


class GameCreate(CreateView):
    model = Game
    fields = ['red_giver', 'red_guesser', 'blue_giver', 'blue_guesser', 'word_set']

    def form_valid(self, form):
        # TODO: check that request.user is one of the players
        form.instance.created_by = self.request.user
        return super(GameCreate, self).form_valid(form)

    def get_success_url(self):
        generate_board(self.object)
        return reverse('game', kwargs={'unique_id': self.object.unique_id})


def generate_colors():
    '''Makes a random set of colors legal for a board
    Counts must be (9, 8, 7, 1) of (red/blue, blue/red, grey, black)
    '''
    rb_counts = [9, 8]
    random.shuffle(rb_counts)
    red_count, blue_count = rb_counts
    grey_count, black_count = 7, 1

    counters = {'red': red_count, 'blue': blue_count,
                'grey': grey_count, 'black': black_count}

    colors = []
    while sum(counters.itervalues()) > 0:
        available_colors = {k: v for k, v in counters.iteritems() if v > 0}
        color = random.choice(available_colors.keys())
        counters[color] -= 1
        colors.append(color)

    return colors


def generate_board(game):
    '''Create a random new board with 25 cards,
     save the board and game'''
    words = list(Word.objects.filter(word_set=game.word_set).order_by('?')[:25])
    colors = generate_colors()
    cards = [Card(word=w, color=colors[idx], game=game) for idx, w in enumerate(words)]
    for c in cards:
        c.save()

    colors = Counter(c.color for c in cards)
    first_color = colors.most_common(1)[0][0]
    game.current_turn = '%s_give' % first_color
    game.red_remaining = colors['red']
    game.blue_remaining = colors['blue']
    game.save()


def find_next_turn(game):
    turn_cycle = cycle(t[0] for t in TURN_STATES)
    t = turn_cycle.next()
    while t != game.current_turn:
        t = turn_cycle.next()
    return turn_cycle.next()


def decrement_card_counter(game, card_color):
    if card_color == 'red':
        game.red_remaining -= 1
    elif card_color == 'blue':
        game.blue_remaining -= 1


def check_game_over(game):
    if game.red_remaining == 0:
        game.winning_team = 'red'
        game.active = False
    elif game.blue_remaining == 0:
        game.winning_team = 'blue'
        game.active = False


@require_http_methods(["POST"])
def guess(request):
    word_id = request.POST['wordId']
    unique_id = request.POST['game_id']
    player = request.POST['player']
    clue_number = int(request.POST['clueNumber'])

    game = get_object_or_404(Game, unique_id=unique_id)
    user = get_object_or_404(User, username=player)
    check_double_post(game, user)

    if word_id:
        word = get_object_or_404(Word, id=word_id.replace('word', ''))
        card = get_object_or_404(Card, word=word, game=game)
        card.chosen = True
        card.save()
    else:
        # User passed
        card = None

    team_color = request.POST['teamColor'].split('_')[0]
    guess = Guess(user=user, guesser_team=team_color, game=game, card=card)
    guess.save()
    if not word_id:
        # User passed
        game.current_turn = find_next_turn(game)
        game.current_guess_number = 0
        game.save()
        return HttpResponseRedirect(
            reverse('game',
                    args=(unique_id,)))
    else:
        game.current_guess_number += 1

    if card.color == 'black':
        # Assassinated!
        game.active = False
        team_choices = {'red', 'blue'}
        other_team = (team_choices - set(team_color)).pop()
        game.winning_team = other_team
    elif (clue_number > 0 and game.current_guess_number >= clue_number + 1) \
            or guess.is_wrong():
        # Note: this greater than also works for '0' unlimited clues
        game.current_turn = find_next_turn(game)
        game.current_guess_number = 0

    decrement_card_counter(game, card.color)
    check_game_over(game)

    game.save()
    return HttpResponseRedirect(
            reverse('game',
                    args=(unique_id,)))


def check_double_post(game, user):
    return user.username != game.current_player().username


@require_http_methods(["POST"])
def give(request):
    text = request.POST['text']
    unique_id = request.POST['game_id']
    player = request.POST['player']

    game = get_object_or_404(Game, unique_id=unique_id)
    user = get_object_or_404(User, username=player)
    if check_double_post(game, user):
        # Player has already given clue, probably a double post
        return HttpResponseRedirect(reverse('game', args=(game.unique_id,)))

    count = request.POST['count']
    clue = Clue(word=text, number=count, giver=user, game=game)
    clue.save()
    game.current_turn = find_next_turn(game)
    game.save()
    return HttpResponseRedirect(reverse('game', args=(unique_id,)))


def find_games(user):
    '''Find all (unique) games with this user, break out by giving and guessing
    Sorted by started date descending'''
    red_givers = list(Game.objects.filter(red_giver=user))
    blue_givers = list(Game.objects.filter(blue_giver=user))
    red_guessers = list(Game.objects.filter(red_guesser=user))
    blue_guessers = list(Game.objects.filter(blue_guesser=user))
    giving = sorted(list(set(red_givers + blue_givers)), key=lambda g: g.started_date, reverse=True)
    guessing = sorted(list(set(red_guessers + blue_guessers)), key=lambda g: g.started_date, reverse=True)
    return giving, guessing


def find_waiting_games(user, giving, guessing):
    '''Return the list of games that are waiting on the given user'''
    return [g for g in (giving + guessing)
            if g.current_player().id == user.id and g.active is True]


@login_required
def profile(request):
    u = request.user
    giving, guessing = find_games(u)
    waiting_on_you = find_waiting_games(u, giving, guessing)
    active_giving = [g for g in giving if g.active is True]
    active_guessing = [g for g in guessing if g.active is True]
    inactive_giving = [g for g in giving if g.active is False]
    inactive_guessing = [g for g in guessing if g.active is False]
    context = {
        'waiting_on_you': waiting_on_you,
        'active': {
            'games_giving': active_giving,
            'games_guessing': active_guessing
        },
        'inactive': {
            'games_giving': inactive_giving,
            'games_guessing': inactive_guessing
        }
    }
    return render(request, 'codenames/profile.html', context)


@require_http_methods(["POST"])
@login_required
def comment(request, comment_id=None):
    if comment_id:
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return JsonResponse({"status": "OK"})

    author = request.user
    text = request.POST['text']
    unique_id = request.POST['game_id']
    color = request.POST['color'].split('_')[0]  # Remove the _give or _guess
    game = get_object_or_404(Game, unique_id=unique_id)
    new_comment = Comment(
        text=text,
        author=author,
        game=game,
        color=color)
    new_comment.save()
    return JsonResponse({"status": "OK"})
