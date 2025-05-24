import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class OdooService {
  String? _sessionId;
  Map<String, String> _headers = {};
  String? baseUrl;

  Future<void> saveSession() async {
    if (_sessionId != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('session_id', _sessionId!);
    }
  }

  Future<void> loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    _sessionId = prefs.getString('session_id');
    if (_sessionId != null) {
      _headers['Cookie'] = 'session_id=$_sessionId';
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('session_id');
    _sessionId = null;
    _headers.remove('Cookie');
  }

  Future<Map<String, dynamic>?> login(String db, String username, String password) async {
    final url = Uri.parse('$baseUrl/web/session/authenticate');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({
        'params': {
          'db': db,
          'login': username,
          'password': password,
        }
      }),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['result']['uid'] != null) {
        // Save session_id from cookies
        final cookies = response.headers['set-cookie'];
        if (cookies != null) {
          final sessionMatch = RegExp('session_id=([^;]+);').firstMatch(cookies);
          if (sessionMatch != null) {
            _sessionId = sessionMatch.group(1);
            _headers['Cookie'] = 'session_id=$_sessionId';
            await saveSession();
          }
        }
        return data['result'];
      }
    }
    return null;
  }
} 