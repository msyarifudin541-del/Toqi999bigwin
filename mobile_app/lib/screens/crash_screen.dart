import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/crash_provider.dart';

class CrashScreen extends StatelessWidget {
  const CrashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => CrashProvider(),
      child: const _CrashView(),
    );
  }
}

class _CrashView extends StatefulWidget {
  const _CrashView();

  @override
  State<_CrashView> createState() => _CrashViewState();
}

class _CrashViewState extends State<_CrashView> with SingleTickerProviderStateMixin {
  late AnimationController _animController;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final crash = Provider.of<CrashProvider>(context);
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        title: const Text('Cross Chicken (Crash)'),
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
            // Recent Multipliers Bar
            SizedBox(
              height: 32,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: crash.history.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (ctx, i) {
                  final mult = crash.history[i];
                  final isHigh = mult >= 3.0;
                  final isMid = mult >= 1.5;
                  final color = isHigh ? const Color(0xFF10B981) : (isMid ? const Color(0xFFF59E0B) : const Color(0xFFEF4444));
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: color.withOpacity(0.4)),
                    ),
                    child: Center(
                      child: Text(
                        '${mult.toStringAsFixed(2)}x',
                        style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),

            // Canvas Arena (Chicken & Highway)
            Container(
              height: 240,
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFF06080E),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFF59E0B), width: 1.5),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  AnimatedBuilder(
                    animation: _animController,
                    builder: (context, child) {
                      return CustomPaint(
                        size: const Size(double.infinity, 240),
                        painter: _HighwayPainter(
                          isRunning: crash.state == CrashGameState.running,
                          offset: _animController.value,
                        ),
                      );
                    },
                  ),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${crash.currentMultiplier.toStringAsFixed(2)}x',
                        style: TextStyle(
                          fontSize: 48,
                          fontWeight: FontWeight.w900,
                          color: crash.state == CrashGameState.busted
                              ? const Color(0xFFEF4444)
                              : const Color(0xFFF59E0B),
                          shadows: const [
                            Shadow(color: Color(0x66F59E0B), blurRadius: 20),
                          ],
                        ),
                      ),
                      if (crash.state == CrashGameState.busted)
                        const Text(
                          'BUSTED!',
                          style: TextStyle(color: Color(0xFFEF4444), fontWeight: FontWeight.bold, letterSpacing: 2),
                        )
                      else if (crash.state == CrashGameState.cashedOut)
                        Text(
                          'CASHED OUT @ ${crash.cashedOutMultiplier?.toStringAsFixed(2)}x (+ \$${crash.winAmount?.toStringAsFixed(2)})',
                          style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold),
                        )
                      else if (crash.state == CrashGameState.running)
                        const Text(
                          'CHICKEN CROSSING HIGHWAY...',
                          style: TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Wager Controls
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0E131F),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('WAGER CHIPS', style: TextStyle(color: Colors.white54, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Row(
                    children: [5.0, 10.0, 25.0, 50.0, 100.0].map((amt) {
                      final isSelected = crash.betAmount == amt;
                      return Expanded(
                        child: GestureDetector(
                          onTap: () => crash.setBetAmount(amt),
                          child: Container(
                            margin: const EdgeInsets.symmetric(horizontal: 2),
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: isSelected ? const Color(0xFFF59E0B) : const Color(0xFF1E293B),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Center(
                              child: Text(
                                '\$${amt.toInt()}',
                                style: TextStyle(
                                  color: isSelected ? Colors.black : Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Launch / Cashout Button
            if (crash.state == CrashGameState.running)
              ElevatedButton(
                onPressed: () async {
                  final newBalance = await crash.cashout();
                  if (newBalance != null) {
                    auth.updateBalance(newBalance);
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 54),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: Text(
                  'CASH OUT @ ${crash.currentMultiplier.toStringAsFixed(2)}x 💰',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              )
            else
              ElevatedButton(
                onPressed: () async {
                  final newBalance = await crash.startRound();
                  if (newBalance != null) {
                    auth.updateBalance(newBalance);
                  }
                  if (crash.errorMessage != null && context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(crash.errorMessage!), backgroundColor: Colors.red),
                    );
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF59E0B),
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 54),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: Text(
                  'START RUN (\$${crash.betAmount.toInt()}) 🐔',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _HighwayPainter extends CustomPainter {
  final bool isRunning;
  final double offset;

  _HighwayPainter({required this.isRunning, required this.offset});

  @override
  void paint(Canvas canvas, Size size) {
    final lanePaint = Paint()
      ..color = const Color(0x3306B6D4)
      ..strokeWidth = 2;

    // Draw horizontal lane dashes
    final lanes = 4;
    for (int i = 1; i < lanes; i++) {
      final y = (size.height / lanes) * i;
      double startX = isRunning ? -offset * 30 : 0;
      while (startX < size.width) {
        canvas.drawLine(
          Offset(startX, y),
          Offset(startX + 15, y),
          lanePaint,
        );
        startX += 30;
      }
    }

    // Draw Chicken in center
    final chickenPaint = Paint()..color = const Color(0xFFFBBF24);
    final center = Offset(size.width * 0.45, size.height * 0.5);
    canvas.drawCircle(center, 16, chickenPaint);

    final combPaint = Paint()..color = const Color(0xFFEF4444);
    canvas.drawCircle(Offset(center.dx, center.dy - 16), 5, combPaint);

    final beakPaint = Paint()..color = const Color(0xFFF97316);
    final path = Path()
      ..moveTo(center.dx + 12, center.dy - 4)
      ..lineTo(center.dx + 22, center.dy)
      ..lineTo(center.dx + 12, center.dy + 4)
      ..close();
    canvas.drawPath(path, beakPaint);
  }

  @override
  bool shouldRepaint(covariant _HighwayPainter oldDelegate) => true;
}
