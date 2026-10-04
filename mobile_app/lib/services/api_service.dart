import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Configurable base URL. Default can switch between local emulator and PWS production.
  static String baseUrl = 'http://10.0.2.2:8000'; // Default Android Emulator (use 127.0.0.1 for iOS/web)

  static void setBaseUrl(String url) {
    baseUrl = url.replaceAll(RegExp(r'/+$'), '');
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  static Future<Map<String, String>> _getHeaders({bool auth = true}) async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (auth) {
      final token = await getToken();
      if (token != null) {
        headers['Authorization'] = 'Token $token';
      }
    }
    return headers;
  }

  // --- Auth APIs ---
  static Future<Map<String, dynamic>> register(
      String username, String password, String email) async {
    final uri = Uri.parse('$baseUrl/api/accounts/register/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(auth: false),
      body: jsonEncode({
        'username': username,
        'password': password,
        'email': email,
      }),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> login(
      String username, String password) async {
    final uri = Uri.parse('$baseUrl/api/accounts/login/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(auth: false),
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getProfile() async {
    final uri = Uri.parse('$baseUrl/api/accounts/profile/');
    final res = await http.get(uri, headers: await _getHeaders());
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> deposit(double amount) async {
    final uri = Uri.parse('$baseUrl/api/accounts/deposit/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({'amount': amount}),
    );
    return jsonDecode(res.body);
  }

  // --- Game APIs ---
  static Future<Map<String, dynamic>> playBaccarat(
      double betAmount, String betChoice) async {
    final uri = Uri.parse('$baseUrl/api/games/baccarat/play/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({
        'bet_amount': betAmount,
        'bet_choice': betChoice,
      }),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> initCrashRound() async {
    final uri = Uri.parse('$baseUrl/api/games/crash/init-round/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({'client_seed': 'toqi999bigwin'}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> placeCrashBet(
      int roundId, double betAmount, double? autoCashout) async {
    final uri = Uri.parse('$baseUrl/api/games/crash/bet/');
    final payload = {
      'round_id': roundId,
      'bet_amount': betAmount,
    };
    if (autoCashout != null) payload['auto_cashout'] = autoCashout;

    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode(payload),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> cashoutCrash(
      int betId, double multiplier) async {
    final uri = Uri.parse('$baseUrl/api/games/crash/cashout/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({
        'bet_id': betId,
        'multiplier': multiplier,
      }),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> finishCrashRound(int roundId) async {
    final uri = Uri.parse('$baseUrl/api/games/crash/finish/');
    final res = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({'round_id': roundId}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getHistory() async {
    final uri = Uri.parse('$baseUrl/api/games/history/');
    final res = await http.get(uri, headers: await _getHeaders());
    return jsonDecode(res.body);
  }
}
