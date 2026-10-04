import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/crash_model.dart';
import '../services/api_service.dart';

enum CrashGameState { idle, running, busted, cashedOut }

class CrashProvider with ChangeNotifier {
  CrashGameState _state = CrashGameState.idle;
  double _currentMultiplier = 1.00;
  double _betAmount = 10.0;
  double? _autoCashout;
  int? _roundId;
  int? _betId;
  double _durationSeconds = 0.0;
  DateTime? _startTime;
  Timer? _ticker;
  double? _cashedOutMultiplier;
  double? _winAmount;
  String? _errorMessage;
  final List<double> _history = [2.45, 14.20, 1.12, 3.80, 1.05];

  CrashGameState get state => _state;
  double get currentMultiplier => _currentMultiplier;
  double get betAmount => _betAmount;
  double? get autoCashout => _autoCashout;
  double? get cashedOutMultiplier => _cashedOutMultiplier;
  double? get winAmount => _winAmount;
  String? get errorMessage => _errorMessage;
  List<double> get history => _history;

  void setBetAmount(double amt) {
    _betAmount = amt;
    notifyListeners();
  }

  void setAutoCashout(double? mult) {
    _autoCashout = mult;
    notifyListeners();
  }

  Future<double?> startRound() async {
    if (_state == CrashGameState.running) return null;
    _errorMessage = null;

    try {
      // 1. Init provably fair round
      final initRes = await ApiService.initCrashRound();
      if (initRes['success'] != true) {
        _errorMessage = 'Failed to init round';
        notifyListeners();
        return null;
      }
      final round = CrashRoundInitModel.fromJson(initRes);
      _roundId = round.roundId;
      _durationSeconds = round.durationSeconds;

      // 2. Place bet
      final betRes = await ApiService.placeCrashBet(_roundId!, _betAmount, _autoCashout);
      if (betRes['success'] != true) {
        _errorMessage = betRes['error'] ?? 'Failed to place bet';
        notifyListeners();
        return null;
      }
      _betId = betRes['bet']['id'];
      final newBalance = (betRes['balance'] as num).toDouble();

      // 3. Start running loop
      _state = CrashGameState.running;
      _currentMultiplier = 1.00;
      _startTime = DateTime.now();
      _cashedOutMultiplier = null;
      _winAmount = null;

      _startTimer();
      notifyListeners();
      return newBalance;

    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  void _startTimer() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(milliseconds: 30), (timer) {
      if (_state != CrashGameState.running || _startTime == null) {
        timer.cancel();
        return;
      }

      final elapsed = DateTime.now().difference(_startTime!).inMilliseconds / 1000.0;
      // Multiplier formula: 1.00 + 0.055 * (t ** 1.72)
      _currentMultiplier = 1.00 + 0.055 * pow(elapsed, 1.72);

      // Check auto cashout
      if (_autoCashout != null && _currentMultiplier >= _autoCashout!) {
        cashout();
      }

      // Check crash
      if (elapsed >= _durationSeconds) {
        _bust();
      } else {
        notifyListeners();
      }
    });
  }

  Future<double?> cashout() async {
    if (_state != CrashGameState.running || _betId == null) return null;
    _ticker?.cancel();

    try {
      final res = await ApiService.cashoutCrash(_betId!, _currentMultiplier);
      if (res['success'] == true) {
        _state = CrashGameState.cashedOut;
        _cashedOutMultiplier = (res['multiplier'] as num).toDouble();
        _winAmount = (res['payout'] as num).toDouble();
        final newBalance = (res['balance'] as num).toDouble();
        notifyListeners();
        return newBalance;
      } else {
        _bust();
      }
    } catch (e) {
      _bust();
    }
    return null;
  }

  void _bust() {
    _ticker?.cancel();
    _state = CrashGameState.busted;
    _history.insert(0, _currentMultiplier);
    if (_history.length > 15) _history.removeLast();

    if (_roundId != null) {
      ApiService.finishCrashRound(_roundId!);
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }
}
