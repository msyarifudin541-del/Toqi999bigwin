import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/auth_provider.dart';
import 'baccarat_screen.dart';
import 'crash_screen.dart';
import 'history_screen.dart';
import 'login_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  void _showDepositDialog(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    double selected = 500.0;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          backgroundColor: const Color(0xFF0E131F),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('Reload Free Chips 🪙', style: TextStyle(color: Color(0xFFF59E0B))),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Select complimentary chip amount:', style: TextStyle(color: Colors.white70)),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                children: [100.0, 500.0, 1000.0, 5000.0].map((amt) {
                  final isSelected = selected == amt;
                  return ChoiceChip(
                    label: Text('\$${amt.toInt()}'),
                    selected: isSelected,
                    selectedColor: const Color(0xFFF59E0B),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.black : Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                    onSelected: (val) {
                      if (val) setState(() => selected = amt);
                    },
                  );
                }).toList(),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
              ),
              onPressed: () async {
                await auth.deposit(selected);
                if (ctx.mounted) Navigator.pop(ctx);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Added \$${selected.toInt()} chips to your wallet!')),
                  );
                }
              },
              child: const Text('Claim Chips'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;
    final currencyFormatter = NumberFormat.currency(symbol: '\$', decimalDigits: 2);

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0E131F),
        elevation: 0,
        title: Row(
          children: [
            const Text('👑', style: TextStyle(fontSize: 20)),
            const SizedBox(width: 8),
            Text(
              user?.username ?? 'TOQI CASINO',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history, color: Colors.white70),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const HistoryScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.redAccent),
            onPressed: () async {
              await auth.logout();
              if (context.mounted) {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                );
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Wallet Balance Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF1E293B), Color(0xFF0E131F)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFF59E0B), width: 1.5),
                boxShadow: const [
                  BoxShadow(color: Color(0x33F59E0B), blurRadius: 15, spreadRadius: 1)
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'WALLET BALANCE',
                        style: TextStyle(color: Colors.white54, fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        currencyFormatter.format(auth.balance),
                        style: const TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFFFCD34D),
                        ),
                      ),
                    ],
                  ),
                  ElevatedButton.icon(
                    onPressed: () => _showDepositDialog(context),
                    icon: const Icon(Icons.add_circle, color: Colors.black, size: 18),
                    label: const Text('Reload', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.black)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFF59E0B),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            const Text(
              'LIVE CASINO ROOMS',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                letterSpacing: 1,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 14),

            // Baccarat Game Card
            InkWell(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const BaccaratScreen()),
                );
              },
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF121826),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF06B6D4), width: 1.2),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0x2206B6D4),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text('🎴', style: TextStyle(fontSize: 32)),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Baccarat (Punto Banco)',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                          SizedBox(height: 4),
                          Text(
                            '8-Deck Shoe • Player, Banker, Tie • Macau Limit',
                            style: TextStyle(color: Colors.white54, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios, color: Color(0xFF06B6D4), size: 18),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Cross Chicken Crash Card
            InkWell(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const CrashScreen()),
                );
              },
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF121826),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFF59E0B), width: 1.2),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0x22F59E0B),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text('🐔', style: TextStyle(fontSize: 32)),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Cross Chicken (Crash)',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Provably Fair • Real-time Multiplier up to 250x',
                            style: TextStyle(color: Colors.white54, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios, color: Color(0xFFF59E0B), size: 18),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
