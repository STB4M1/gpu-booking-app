import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/reservation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const baseUrl = "https://4fca-182-167-109-2.ngrok-free.app/api/reservations";

  // 🔐 ヘッダーにトークンを自動で追加
  static Future<Map<String, String>> _getAuthHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      throw Exception('⚠️ トークンが見つかりません。ログインしてください。');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  static Future<Reservation> sendNaturalText(String text) async {
    final url = Uri.parse("$baseUrl/natural");
    final headers = await _getAuthHeaders();

    final response = await http.post(
      url,
      headers: headers,
      body: jsonEncode({"text": text}),
    ).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      return Reservation.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception("サーバーエラー: ${response.statusCode}");
    }
  }

  static Future<Map<String, dynamic>> sendTestRequest(String text) async {
    final url = Uri.parse("$baseUrl/test-flutter");
    final headers = await _getAuthHeaders();

    final response = await http.post(
      url,
      headers: headers,
      body: jsonEncode({"text": text}),
    ).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception("ステータスコード: ${response.statusCode}");
    }
  }

  static Future<List<Reservation>> fetchReservations() async {
    final url = Uri.parse("$baseUrl/me");
    final headers = await _getAuthHeaders();

    final response = await http.get(url, headers: headers).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(utf8.decode(response.bodyBytes));
      return jsonList.map((json) => Reservation.fromJson(json)).toList();
    } else {
      throw Exception("予約一覧取得失敗: ${response.statusCode}");
    }
  }

  static Future<List<Reservation>> fetchPendingConflicts() async {
    final url = Uri.parse("$baseUrl/conflicts");
    final headers = await _getAuthHeaders();

    final response = await http.get(url, headers: headers).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(utf8.decode(response.bodyBytes));
      return jsonList.map((json) => Reservation.fromJson(json)).toList();
    } else {
      throw Exception("保留中予約の取得失敗: ${response.statusCode}");
    }
  }

  static Future<void> confirmCancelReservation(int reservationId) async {
    final url = Uri.parse("$baseUrl/$reservationId/confirm-cancel");
    final headers = await _getAuthHeaders();

    final response = await http.patch(url, headers: headers).timeout(const Duration(seconds: 5));

    if (response.statusCode != 200) {
      throw Exception("予約の承諾処理に失敗しました: ${response.statusCode}");
    }
  }
}
