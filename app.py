import json
import os
import random
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deck = db.Column(db.Text, nullable=False)
    player_hand = db.Column(db.Text, nullable=False)
    dealer_hand = db.Column(db.Text, nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
    result = db.Column(db.String(20))

    def get_deck(self):
        return json.loads(self.deck)

    def set_deck(self, deck_list):
        self.deck = json.dumps(deck_list)

    def get_player_hand(self):
        return json.loads(self.player_hand)

    def set_player_hand(self, hand):
        self.player_hand = json.dumps(hand)

    def get_dealer_hand(self):
        return json.loads(self.dealer_hand)

    def set_dealer_hand(self, hand):
        self.dealer_hand = json.dumps(hand)

# Helper Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Game Logic Helpers
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'suit': s, 'rank': r} for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def calculate_hand(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card['rank']
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            aces += 1
            value += 11
        else:
            value += int(rank)

    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = float(request.form.get('amount', 0))
    if amount > 0:
        user = db.session.get(User, session['user_id'])
        user.balance += amount
        db.session.commit()
        flash(f'Deposited ${amount}')
    return redirect(url_for('dashboard'))

# Game API
@app.route('/game/start', methods=['POST'])
@login_required
def start_game():
    user = db.session.get(User, session['user_id'])
    data = request.json
    bet = float(data.get('bet', 10))

    if user.balance < bet:
        return jsonify({'error': 'Insufficient funds'}), 400

    user.balance -= bet

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    game = Game(
        user_id=user.id,
        bet_amount=bet,
        status='active'
    )
    game.set_deck(deck)
    game.set_player_hand(player_hand)
    game.set_dealer_hand(dealer_hand)

    db.session.add(game)
    db.session.commit()

    # Check for immediate Blackjack
    player_val = calculate_hand(player_hand)
    if player_val == 21:
        # Payout 3:2 immediately if dealer doesn't have 21?
        # For simplicity let's handle it in the 'hit/stand' loop or just let client know.
        # But actually standard blackjack checks immediately.
        # I'll just return the state and let the client call 'stand' or handle it.
        pass

    return jsonify({
        'game_id': game.id,
        'player_hand': player_hand,
        'dealer_card': dealer_hand[0], # Show only one card
        'player_value': calculate_hand(player_hand),
        'balance': user.balance
    })

@app.route('/game/hit', methods=['POST'])
@login_required
def hit():
    data = request.json
    game_id = data.get('game_id')
    game = db.session.get(Game, game_id)

    if not game or game.status != 'active' or game.user_id != session['user_id']:
        return jsonify({'error': 'Invalid game'}), 400

    deck = game.get_deck()
    player_hand = game.get_player_hand()

    new_card = deck.pop()
    player_hand.append(new_card)

    game.set_deck(deck)
    game.set_player_hand(player_hand)

    player_val = calculate_hand(player_hand)

    if player_val > 21:
        game.status = 'finished'
        game.result = 'lose'
        db.session.commit()
        return jsonify({
            'status': 'finished',
            'result': 'lose',
            'player_hand': player_hand,
            'player_value': player_val,
            'dealer_hand': game.get_dealer_hand() # Reveal dealer
        })

    db.session.commit()

    return jsonify({
        'status': 'active',
        'player_hand': player_hand,
        'player_value': player_val,
        'dealer_card': game.get_dealer_hand()[0]
    })

@app.route('/game/stand', methods=['POST'])
@login_required
def stand():
    data = request.json
    game_id = data.get('game_id')
    game = db.session.get(Game, game_id)

    if not game or game.status != 'active' or game.user_id != session['user_id']:
        return jsonify({'error': 'Invalid game'}), 400

    deck = game.get_deck()
    dealer_hand = game.get_dealer_hand()

    # Dealer logic: hit until 17
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    game.set_deck(deck)
    game.set_dealer_hand(dealer_hand)
    game.status = 'finished'

    player_val = calculate_hand(game.get_player_hand())
    dealer_val = calculate_hand(dealer_hand)

    user = db.session.get(User, session['user_id'])

    result = ''
    if dealer_val > 21:
        result = 'win'
        user.balance += game.bet_amount * 2
    elif player_val > dealer_val:
        result = 'win'
        user.balance += game.bet_amount * 2
    elif player_val == dealer_val:
        result = 'push'
        user.balance += game.bet_amount
    else:
        result = 'lose'

    game.result = result
    db.session.commit()

    return jsonify({
        'status': 'finished',
        'result': result,
        'player_hand': game.get_player_hand(),
        'player_value': player_val,
        'dealer_hand': dealer_hand,
        'dealer_value': dealer_val,
        'balance': user.balance
    })

# Database Init
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
