class BetModel {
  final int id;
  final String username;
  final String gameType;
  final double betAmount;
  final String betChoice;
  final double? autoCashout;
  final double? cashedOutAt;
  final double payout;
  final String status;
  final String createdAt;

  BetModel({
    required this.id,
    required this.username,
    required this.gameType,
    required this.betAmount,
    required this.betChoice,
    this.autoCashout,
    this.cashedOutAt,
    required this.payout,
    required this.status,
    required this.createdAt,
  });

  factory BetModel.fromJson(Map<String, dynamic> json) {
    final gameRound = json['game_round'] is Map ? json['game_round'] : {};
    return BetModel(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      gameType: gameRound['game_type']?.toString() ?? 'GAME',
      betAmount: (json['bet_amount'] is num)
          ? (json['bet_amount'] as num).toDouble()
          : double.tryParse(json['bet_amount']?.toString() ?? '0') ?? 0.0,
      betChoice: json['bet_choice']?.toString() ?? '',
      autoCashout: json['auto_cashout'] != null
          ? double.tryParse(json['auto_cashout'].toString())
          : null,
      cashedOutAt: json['cashed_out_at'] != null
          ? double.tryParse(json['cashed_out_at'].toString())
          : null,
      payout: (json['payout'] is num)
          ? (json['payout'] as num).toDouble()
          : double.tryParse(json['payout']?.toString() ?? '0') ?? 0.0,
      status: json['status']?.toString() ?? 'PENDING',
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}
