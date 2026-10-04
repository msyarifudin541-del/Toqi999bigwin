import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  UserModel? _user;
  String? _token;
  bool _isLoading = false;
  String? _errorMessage;

  UserModel? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null && _user != null;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  double get balance => _user?.wallet.balance ?? 0.0;

  Future<bool> checkAuth() async {
    _isLoading = true;
    notifyListeners();
    try {
      final savedToken = await ApiService.getToken();
      if (savedToken != null) {
        _token = savedToken;
        final res = await ApiService.getProfile();
        if (res['success'] == true && res['user'] != null) {
          _user = UserModel.fromJson(res['user']);
          _isLoading = false;
          notifyListeners();
          return true;
        }
      }
    } catch (e) {
      _errorMessage = e.toString();
    }
    _token = null;
    _user = null;
    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await ApiService.login(username, password);
      if (res['success'] == true) {
        _token = res['token'];
        _user = UserModel.fromJson(res['user']);
        await ApiService.saveToken(_token!);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = res['errors']?.toString() ?? 'Login failed';
      }
    } catch (e) {
      _errorMessage = 'Network connection failed: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> register(String username, String password, String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await ApiService.register(username, password, email);
      if (res['success'] == true) {
        _token = res['token'];
        _user = UserModel.fromJson(res['user']);
        await ApiService.saveToken(_token!);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = res['errors']?.toString() ?? 'Registration failed';
      }
    } catch (e) {
      _errorMessage = 'Network connection failed: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> deposit(double amount) async {
    try {
      final res = await ApiService.deposit(amount);
      if (res['success'] == true && res['balance'] != null) {
        updateBalance((res['balance'] as num).toDouble());
        return true;
      }
    } catch (e) {
      _errorMessage = e.toString();
    }
    return false;
  }

  void updateBalance(double newBalance) {
    if (_user != null) {
      _user = UserModel(
        id: _user!.id,
        username: _user!.username,
        email: _user!.email,
        wallet: WalletModel(
          id: _user!.wallet.id,
          balance: newBalance,
          createdAt: _user!.wallet.createdAt,
          updatedAt: DateTime.now().toIso8601String(),
        ),
      );
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await ApiService.clearToken();
    _token = null;
    _user = null;
    notifyListeners();
  }
}
