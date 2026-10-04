import 'package:flutter/foundation.dart';
import '../models/baccarat_model.dart';
import '../services/api_service.dart';

class BaccaratProvider with ChangeNotifier {
  double _selectedChip = 10.0;
  String _selectedChoice = 'PLAYER'; // 'PLAYER', 'BANKER', 'TIE'
  bool _isDealing = false;
  BaccaratResultModel? _lastResult;
  Map<String, dynamic>? _payoutInfo;
  String? _errorMessage;
  final List<String> _historyBeads = [];

  double get selectedChip => _selectedChip;
  String get selectedChoice => _selectedChoice;
  bool get isDealing => _isDealing;
  BaccaratResultModel? get lastResult => _lastResult;
  Map<String, dynamic>? get payoutInfo => _payoutInfo;
  String? get errorMessage => _errorMessage;
  List<String> get historyBeads => _historyBeads;

  void selectChip(double chip) {
    _selectedChip = chip;
    notifyListeners();
  }

  void selectChoice(String choice) {
    _selectedChoice = choice;
    notifyListeners();
  }

  Future<double?> deal() async {
    _isDealing = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await ApiService.playBaccarat(_selectedChip, _selectedChoice);
      if (res['success'] == true) {
        _lastResult = BaccaratResultModel.fromJson(res['result']);
        _payoutInfo = res['payout_info'];
        _historyBeads.insert(0, _lastResult!.winner);
        if (_historyBeads.length > 20) _historyBeads.removeLast();

        _isDealing = false;
        notifyListeners();
        return (res['balance'] as num).toDouble();
      } else {
        _errorMessage = res['error'] ?? 'Deal failed';
      }
    } catch (e) {
      _errorMessage = e.toString();
    }

    _isDealing = false;
    notifyListeners();
    return null;
  }
}
