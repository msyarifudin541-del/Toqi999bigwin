import 'package:flutter/material.dart';
import '../models/game_model.dart';
import '../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _loading = true;
  List<BetModel> _bets = [];

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  void _fetch() async {
    try {
      final res = await ApiService.getHistory();
      if (res['success'] == true && res['history'] != null) {
        final list = res['history'] as List;
        setState(() {
          _bets = list.map((b) => BetModel.fromJson(b)).toList();
          _loading = false;
        });
        return;
      }
    } catch (_) {}
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        title: const Text('Game History'),
        backgroundColor: const Color(0xFF0E131F),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFF59E0B)))
          : _bets.isEmpty
              ? const Center(
                  child: Text('No bets found', style: TextStyle(color: Colors.white54)),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _bets.length,
                  itemBuilder: (ctx, i) {
                    final bet = _bets[i];
                    final isWon = bet.status == 'WON' || bet.status == 'CASHED_OUT';
                    return Container(
                      margin: const EdgeInsets.bottom: 12,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF121826),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                bet.gameType,
                                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Choice: ${bet.betChoice} • Wager: \$${bet.betAmount.toStringAsFixed(2)}',
                                style: const TextStyle(color: Colors.white54, fontSize: 12),
                              ),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                bet.status,
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isWon ? const Color(0xFF10B981) : Colors.redAccent,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                isWon ? '+\$${bet.payout.toStringAsFixed(2)}' : '\$0.00',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isWon ? const Color(0xFF10B981) : Colors.white38,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
