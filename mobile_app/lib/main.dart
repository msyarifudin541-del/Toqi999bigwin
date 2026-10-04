import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'screens/dashboard_screen.dart';
import 'screens/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const Toqi999BigwinApp());
}

class Toqi999BigwinApp extends StatelessWidget {
  const Toqi999BigwinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        title: 'Toqi999bigwin',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          brightness: Brightness.dark,
          primaryColor: const Color(0xFFF59E0B),
          scaffoldBackgroundColor: const Color(0xFF07090E),
          colorScheme: const ColorScheme.dark(
            primary: Color(0xFFF59E0B),
            secondary: Color(0xFF06B6D4),
            surface: Color(0xFF0E131F),
            background: Color(0xFF07090E),
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF0E131F),
            elevation: 0,
            centerTitle: true,
          ),
        ),
        home: const _RootDecider(),
      ),
    );
  }
}

class _RootDecider extends StatefulWidget {
  const _RootDecider();

  @override
  State<_RootDecider> createState() => _RootDeciderState();
}

class _RootDeciderState extends State<_RootDecider> {
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _init();
  }

  void _init() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    await auth.checkAuth();
    if (mounted) {
      setState(() => _checking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        backgroundColor: Color(0xFF07090E),
        body: Center(
          child: CircularProgressIndicator(color: Color(0xFFF59E0B)),
        ),
      );
    }

    final auth = Provider.of<AuthProvider>(context);
    return auth.isAuthenticated ? const DashboardScreen() : const LoginScreen();
  }
}
