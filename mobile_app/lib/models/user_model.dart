class WalletModel {
  final int id;
  final double balance;
  final String createdAt;
  final String updatedAt;

  WalletModel({
    required this.id,
    required this.balance,
    required this.createdAt,
    required this.updatedAt,
  });

  factory WalletModel.fromJson(Map<String, dynamic> json) {
    return WalletModel(
      id: json['id'] ?? 0,
      balance: (json['balance'] is num)
          ? (json['balance'] as num).toDouble()
          : double.tryParse(json['balance']?.toString() ?? '0') ?? 0.0,
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'balance': balance,
        'created_at': createdAt,
        'updated_at': updatedAt,
      };
}

class UserModel {
  final int id;
  final String username;
  final String email;
  final WalletModel wallet;

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.wallet,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      wallet: WalletModel.fromJson(json['wallet'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'username': username,
        'email': email,
        'wallet': wallet.toJson(),
      };
}
