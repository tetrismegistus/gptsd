from random import shuffle

from modules.tarotdeck import TarotDeck

class TarotHandler:
    def __init__(self):
        self.max_cards = 3
        self.decks = ('jodocamoin', 'riderwaitesmith', 'crowleythoth')

    def draw(self, num=1, deck_type='jodocamoin'):
        response_text = []
        images = []
        if deck_type not in self.decks:
            response_text.append("Deck type must be one of {}".format(self.decks))
        elif num > self.max_cards:
            response_text.append("I will draw a max of {} cards.".format(self.max_cards))
        else:
            deck = TarotDeck(deck_type)
            shuffle(deck)
            num_cards = num
            for c in range(num_cards):
                card = deck.pop()
                if 'majors' not in card.image:
                    response_text.append(card.rank + ' of ' + card.kind)
                else:
                    response_text.append(card.rank + ': ' + card.kind)
                images.append(card.image)
        return response_text, images



