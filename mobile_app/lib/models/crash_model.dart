class CrashRoundInitModel {
  final int roundId;
  final String serverSeedHash;
  final String clientSeed;
  final int nonce;
  final double durationSeconds;

  CrashRoundInitModel({
    required this.roundId,
    required this.serverSeedHash,
    required this.clientSeed,
    required this.nonce,
    required this.durationSeconds,
  });

  factory CrashRoundInitModel.fromJson(Map<String, dynamic> json) {
    return CrashRoundInitModel(
      roundId: json['round_id'] ?? 0,
      serverSeedHash: json['server_seed_hash'] ?? '',
      clientSeed: json['client_seed'] ?? '',
      nonce: json['nonce'] ?? 1,
      durationSeconds: (json['duration_seconds'] is num)
          ? (json['duration_seconds'] as num).toDouble()
          : double.tryParse(json['duration_seconds']?.toString() ?? '0') ?? 0.0,
    );
  }
}
