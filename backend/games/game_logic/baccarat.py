"""
Baccarat (Punto Banco) Engine.
Implements official international casino rules with 8-deck shoe and third-card tableau.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

CARD_VALUES = {
    'A': 1,
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 0, 'J': 0, 'Q': 0, 'K': 0
}

@dataclass
class Card:
    suit: str
    rank: str

    @property
    def value(self) -> int:
        return CARD_VALUES[self.rank]

    @property
    def color(self) -> str:
        return 'red' if self.suit in ['♥', '♦'] else 'black'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'suit': self.suit,
            'rank': self.rank,
            'value': self.value,
            'color': self.color,
            'display': f"{self.rank}{self.suit}"
        }


class Hand:
    def __init__(self, name: str):
        self.name = name
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        self.cards.append(card)

    @property
    def score(self) -> int:
        return sum(c.value for c in self.cards) % 10

    @property
    def is_natural(self) -> bool:
        return len(self.cards) == 2 and self.score in [8, 9]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'cards': [c.to_dict() for c in self.cards],
            'score': self.score,
            'is_natural': self.is_natural
        }


@dataclass
class BaccaratResult:
    player_hand: Hand
    banker_hand: Hand
    winner: str  # 'PLAYER', 'BANKER', 'TIE'
    natural: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'player': self.player_hand.to_dict(),
            'banker': self.banker_hand.to_dict(),
            'winner': self.winner,
            'natural': self.natural,
            'summary': self.summary
        }


class BaccaratEngine:
    """Manages shoe and executes Punto Banco rounds."""

    def __init__(self, num_decks: int = 8):
        self.num_decks = num_decks
        self.shoe: List[Card] = []
        self._shuffle_shoe()

    def _shuffle_shoe(self):
        cards = [Card(suit=s, rank=r) for s in SUITS for r in RANKS for _ in range(self.num_decks)]
        random.shuffle(cards)
        self.shoe = cards

    def deal_card(self) -> Card:
        if len(self.shoe) < 16:
            self._shuffle_shoe()
        return self.shoe.pop()

    def play_round(self) -> BaccaratResult:
        player = Hand("Player")
        banker = Hand("Banker")

        # Initial 4 cards dealt alternately
        player.add_card(self.deal_card())
        banker.add_card(self.deal_card())
        player.add_card(self.deal_card())
        banker.add_card(self.deal_card())

        # Check for natural 8 or 9
        if player.is_natural or banker.is_natural:
            winner = self._determine_winner(player.score, banker.score)
            summary = f"Natural {max(player.score, banker.score)}! {winner.capitalize()} wins."
            if winner == 'TIE':
                summary = f"Natural Tie at {player.score}!"
            return BaccaratResult(
                player_hand=player,
                banker_hand=banker,
                winner=winner,
                natural=True,
                summary=summary
            )

        # Player third-card rule
        player_drew = False
        p3_card: Optional[Card] = None

        if player.score in [0, 1, 2, 3, 4, 5]:
            p3_card = self.deal_card()
            player.add_card(p3_card)
            player_drew = True

        # Banker third-card rule
        banker_drew = False
        if not player_drew:
            # When player stands on 6 or 7, banker draws on 0-5, stands on 6-7
            if banker.score in [0, 1, 2, 3, 4, 5]:
                banker.add_card(self.deal_card())
                banker_drew = True
        else:
            # Player drew a 3rd card; banker follows tableau based on player's 3rd card rank value
            p3_val = p3_card.value
            b_score = banker.score

            draw_banker = False
            if b_score in [0, 1, 2]:
                draw_banker = True
            elif b_score == 3 and p3_val != 8:
                draw_banker = True
            elif b_score == 4 and p3_val in [2, 3, 4, 5, 6, 7]:
                draw_banker = True
            elif b_score == 5 and p3_val in [4, 5, 6, 7]:
                draw_banker = True
            elif b_score == 6 and p3_val in [6, 7]:
                draw_banker = True

            if draw_banker:
                banker.add_card(self.deal_card())
                banker_drew = True

        winner = self._determine_winner(player.score, banker.score)
        if winner == 'TIE':
            summary = f"Tie game at {player.score}!"
        else:
            summary = f"{winner.capitalize()} wins with {player.score if winner == 'PLAYER' else banker.score} vs {banker.score if winner == 'PLAYER' else player.score}."

        return BaccaratResult(
            player_hand=player,
            banker_hand=banker,
            winner=winner,
            natural=False,
            summary=summary
        )

    @staticmethod
    def _determine_winner(player_score: int, banker_score: int) -> str:
        if player_score > banker_score:
            return 'PLAYER'
        elif banker_score > player_score:
            return 'BANKER'
        return 'TIE'

    @staticmethod
    def calculate_payout(bet_choice: str, bet_amount: float, winner: str) -> Dict[str, Any]:
        """
        Calculates profit, total return, and status for a bet.
        bet_choice: 'PLAYER', 'BANKER', 'TIE'
        """
        bet_choice = bet_choice.upper()
        if winner == 'TIE':
            if bet_choice == 'TIE':
                # Tie pays 8:1 (profit = 8 * bet, return = 9 * bet)
                profit = bet_amount * 8.0
                total_return = bet_amount * 9.0
                return {'status': 'WON', 'profit': profit, 'total_return': total_return, 'description': 'Tie Win (8:1)'}
            else:
                # Player/Banker bets are pushed (refunded)
                return {'status': 'PUSH', 'profit': 0.0, 'total_return': bet_amount, 'description': 'Tie Push (Refund)'}

        if bet_choice == winner:
            if bet_choice == 'PLAYER':
                # Player pays 1:1
                profit = bet_amount * 1.0
                total_return = bet_amount * 2.0
                return {'status': 'WON', 'profit': profit, 'total_return': total_return, 'description': 'Player Win (1:1)'}
            elif bet_choice == 'BANKER':
                # Banker pays 0.95:1 (5% commission)
                profit = round(bet_amount * 0.95, 2)
                total_return = round(bet_amount * 1.95, 2)
                return {'status': 'WON', 'profit': profit, 'total_return': total_return, 'description': 'Banker Win (0.95:1)'}

        return {'status': 'LOST', 'profit': -bet_amount, 'total_return': 0.0, 'description': 'Loss'}
