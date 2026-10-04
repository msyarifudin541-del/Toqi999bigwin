class BaccaratCardModel {
  final String suit;
  final String rank;
  final int value;
  final String color;
  final String display;

  BaccaratCardModel({
    required this.suit,
    required this.rank,
    required this.value,
    required this.color,
    required this.display,
  });

  factory BaccaratCardModel.fromJson(Map<String, dynamic> json) {
    return BaccaratCardModel(
      suit: json['suit'] ?? '',
      rank: json['rank'] ?? '',
      value: json['value'] ?? 0,
      color: json['color'] ?? 'black',
      display: json['display'] ?? '',
    );
  }
}

class BaccaratHandModel {
  final String name;
  final List<BaccaratCardModel> cards;
  final int score;
  final bool isNatural;

  BaccaratHandModel({
    required this.name,
    required this.cards,
    required this.score,
    required this.isNatural,
  });

  factory BaccaratHandModel.fromJson(Map<String, dynamic> json) {
    final list = json['cards'] as List? ?? [];
    return BaccaratHandModel(
      name: json['name'] ?? '',
      cards: list.map((c) => BaccaratCardModel.fromJson(c)).toList(),
      score: json['score'] ?? 0,
      isNatural: json['is_natural'] ?? false,
    );
  }
}

class BaccaratResultModel {
  final BaccaratHandModel player;
  final BaccaratHandModel banker;
  final String winner;
  final bool natural;
  final String summary;

  BaccaratResultModel({
    required this.player,
    required this.banker,
    required this.winner,
    required this.natural,
    required this.summary,
  });

  factory BaccaratResultModel.fromJson(Map<String, dynamic> json) {
    return BaccaratResultModel(
      player: BaccaratHandModel.fromJson(json['player'] ?? {}),
      banker: BaccaratHandModel.fromJson(json['banker'] ?? {}),
      winner: json['winner'] ?? 'TIE',
      natural: json['natural'] ?? false,
      summary: json['summary'] ?? '',
    );
  }
}
