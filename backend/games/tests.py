from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from games.game_logic.baccarat import BaccaratEngine, Card, Hand
from games.game_logic.crash import ProvablyFair, CrashEngine

class GameEngineTests(TestCase):
    def test_baccarat_card_values(self):
        self.assertEqual(Card('♠', 'A').value, 1)
        self.assertEqual(Card('♥', '9').value, 9)
        self.assertEqual(Card('♦', 'K').value, 0)
        self.assertEqual(Card('♣', '10').value, 0)

    def test_baccarat_hand_scores(self):
        h = Hand("Test")
        h.add_card(Card('♠', '8'))
        h.add_card(Card('♥', '9'))
        self.assertEqual(h.score, 7)  # (8 + 9) % 10 = 7

        h2 = Hand("Natural")
        h2.add_card(Card('♠', '4'))
        h2.add_card(Card('♥', '5'))
        self.assertEqual(h2.score, 9)
        self.assertTrue(h2.is_natural)

    def test_baccarat_round_execution(self):
        engine = BaccaratEngine()
        result = engine.play_round()
        self.assertIn(result.winner, ['PLAYER', 'BANKER', 'TIE'])
        self.assertGreaterEqual(result.player_hand.score, 0)
        self.assertLessEqual(result.player_hand.score, 9)
        self.assertGreaterEqual(result.banker_hand.score, 0)
        self.assertLessEqual(result.banker_hand.score, 9)

    def test_baccarat_payout_calculation(self):
        # Player win
        p = BaccaratEngine.calculate_payout('PLAYER', 100.0, 'PLAYER')
        self.assertEqual(p['status'], 'WON')
        self.assertEqual(p['total_return'], 200.0)

        # Banker win (5% comm)
        b = BaccaratEngine.calculate_payout('BANKER', 100.0, 'BANKER')
        self.assertEqual(b['status'], 'WON')
        self.assertEqual(b['total_return'], 195.0)

        # Tie win
        t = BaccaratEngine.calculate_payout('TIE', 100.0, 'TIE')
        self.assertEqual(t['status'], 'WON')
        self.assertEqual(t['total_return'], 900.0)

        # Tie push for Player bet
        push = BaccaratEngine.calculate_payout('PLAYER', 100.0, 'TIE')
        self.assertEqual(push['status'], 'PUSH')
        self.assertEqual(push['total_return'], 100.0)

    def test_crash_provably_fair_deterministic(self):
        server_seed = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        client_seed = "test-client-seed"
        nonce = 42

        mult1, hash1 = ProvablyFair.generate_crash_point(server_seed, client_seed, nonce)
        mult2, hash2 = ProvablyFair.generate_crash_point(server_seed, client_seed, nonce)

        self.assertEqual(mult1, mult2)
        self.assertEqual(hash1, hash2)
        self.assertGreaterEqual(mult1, 1.00)

        verification = ProvablyFair.verify(server_seed, client_seed, nonce)
        self.assertTrue(verification['verified'])
        self.assertEqual(verification['crash_point'], mult1)
