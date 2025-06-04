import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/reservation.dart';

class ApiService {
  static const baseUrl = "https://b710-182-167-109-2.ngrok-free.app/api/reservations";

  static Future<Reservation> sendNaturalText(String text) async {
    final url = Uri.parse("$baseUrl/natural");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"text": text}),
    ).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      return Reservation.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception("サーバーエラー: ${response.statusCode}");
    }
  }

  // 🧪 テスト用エンドポイント（FastAPIがFlutterから受け取るだけ）
  static Future<Map<String, dynamic>> sendTestRequest(String text) async {
    final url = Uri.parse("$baseUrl/test-flutter");

    final response = await http
        .post(
          url,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"text": text}),
        )
        .timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception("ステータスコード: ${response.statusCode}");
    }
  }

  static Future<List<Reservation>> fetchReservations() async {
    final url = Uri.parse("$baseUrl/me");

    final response = await http.get(url).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(utf8.decode(response.bodyBytes));
      return jsonList.map((json) => Reservation.fromJson(json)).toList();
    } else {
      throw Exception("予約一覧取得失敗: ${response.statusCode}");
    }
  }
}


