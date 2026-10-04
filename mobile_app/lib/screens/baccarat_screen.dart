import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/baccarat_provider.dart';
import '../models/baccarat_model.dart';

class BaccaratScreen extends StatelessWidget {
  const BaccaratScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => BaccaratProvider(),
      child: const _BaccaratView(),
    );
  }
}

class _BaccaratView extends StatelessWidget {
  const _BaccaratView();

  Widget _buildCard(BaccaratCardModel card) {
    final isRed = card.color == 'red';
    return Container(
      width: 48,
      height: 70,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(6),
        boxShadow: const [BoxShadow(color: Colors.black54, blurRadius: 4)],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Align(
            alignment: Alignment.topLeft,
            child: Text(
              card.rank,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: isRed ? Colors.red : Colors.black,
              ),
            ),
          ),
          Text(
            card.suit,
            style: TextStyle(fontSize: 16, color: isRed ? Colors.red : Colors.black),
          ),
          Align(
            alignment: Alignment.bottomRight,
            child: Text(
              card.rank,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: isRed ? Colors.red : Colors.black,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHandBox(String title, BaccaratHandModel? hand, Color accent) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF0E131F),
          borderRadius: BorderRadius.circular(12),
          border: Border(top: BorderSide(color: accent, width: 3)),
        ),
        child: Column(
          children: [
            Text(
              title,
              style: TextStyle(color: accent, fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: hand?.cards.map((c) => _buildCard(c)).toList() ?? [
                _buildPlaceholderCard(),
                _buildPlaceholderCard(),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              hand?.score.toString() ?? '0',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholderCard() {
    return Container(
      width: 48,
      height: 70,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.white12),
      ),
      child: const Center(
        child: Text('🂠', style: TextStyle(color: Colors.white24, fontSize: 20)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final baccarat = Provider.of<BaccaratProvider>(context);
    final auth = Provider.of<AuthProvider>(context);
    final lastResult = baccarat.lastResult;

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        title: const Text('Baccarat (Punto Banco)'),
        backgroundColor: const Color(0xFF0E131F),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                '🪙 \$${auth.balance.toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFFCD34D)),
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Winner Banner
            if (lastResult != null)
              Container(
                margin: const EdgeInsets.bottom: 16,
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                decoration: BoxDecoration(
                  color: lastResult.winner == 'TIE'
                      ? const Color(0x3310B981)
                      : (baccarat.payoutInfo?['status'] == 'WON' ? const Color(0x3310B981) : const Color(0x33EF4444)),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFF59E0B)),
                ),
                child: Text(
                  lastResult.summary.toUpperCase(),
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 13),
                ),
              ),

            // Hands Area
            Row(
              children: [
                _buildHandBox('PLAYER', lastResult?.player, const Color(0xFF06B6D4)),
                const SizedBox(width: 12),
                _buildHandBox('BANKER', lastResult?.banker, const Color(0xFFEF4444)),
              ],
            ),
            const SizedBox(height: 24),

            // Betting Zone Selector
            Row(
              children: [
                _buildBetChoiceBtn(context, 'PLAYER', '1 : 1', const Color(0xFF06B6D4)),
                const SizedBox(width: 8),
                _buildBetChoiceBtn(context, 'TIE', '8 : 1', const Color(0xFF10B981)),
                const SizedBox(width: 8),
                _buildBetChoiceBtn(context, 'BANKER', '0.95 : 1', const Color(0xFFEF4444)),
              ],
            ),
            const SizedBox(height: 24),

            // Chip Selector
            const Align(
              alignment: Alignment.centerLeft,
              child: Text('SELECT CHIP WAGER', style: TextStyle(color: Colors.white54, fontSize: 12, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [1.0, 5.0, 10.0, 25.0, 100.0, 500.0].map((chip) {
                final isSelected = baccarat.selectedChip == chip;
                return GestureDetector(
                  onTap: () => baccarat.selectChip(chip),
                  child: Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isSelected ? const Color(0xFFF59E0B) : const Color(0xFF121826),
                      border: Border.all(
                        color: isSelected ? Colors.white : const Color(0xFFF59E0B),
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        '\$${chip.toInt()}',
                        style: TextStyle(
                          color: isSelected ? Colors.black : const Color(0xFFF59E0B),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 32),

            // Deal Button
            ElevatedButton(
              onPressed: baccarat.isDealing
                  ? null
                  : () async {
                      final newBalance = await baccarat.deal();
                      if (newBalance != null) {
                        auth.updateBalance(newBalance);
                      }
                      if (baccarat.errorMessage != null && context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(baccarat.errorMessage!), backgroundColor: Colors.red),
                        );
                      }
                    },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF59E0B),
                foregroundColor: Colors.black,
                minimumSize: const Size(double.infinity, 50),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: baccarat.isDealing
                  ? const CircularProgressIndicator(color: Colors.black)
                  : Text(
                      'DEAL (\$${baccarat.selectedChip.toInt()}) 🎴',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBetChoiceBtn(BuildContext context, String choice, String payout, Color color) {
    final baccarat = Provider.of<BaccaratProvider>(context);
    final isSelected = baccarat.selectedChoice == choice;

    return Expanded(
      child: GestureDetector(
        onTap: () => baccarat.selectChoice(choice),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.2) : const Color(0xFF121826),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected ? color : Colors.white12,
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Text(
                choice,
                style: TextStyle(fontWeight: FontWeight.w900, color: color, fontSize: 14),
              ),
              const SizedBox(height: 2),
              Text(payout, style: const TextStyle(color: Colors.white38, fontSize: 10)),
            ],
          ),
        ),
      ),
    );
  }
}
