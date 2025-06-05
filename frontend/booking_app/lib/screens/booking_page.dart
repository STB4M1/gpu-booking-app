import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'reservation_list_page.dart';
import 'conflict_page.dart';
import 'package:shared_preferences/shared_preferences.dart';

class BookingPage extends StatefulWidget {
  const BookingPage({super.key});

  @override
  State<BookingPage> createState() => _BookingPageState();
}

class _BookingPageState extends State<BookingPage> {
  final TextEditingController _controller = TextEditingController();
  String _result = "";

  Future<void> sendText() async {
    final text = _controller.text;
    print("📤 入力文を送信します: $text");

    try {
      // ✅ 本番用：Colab経由で構造化 → DB登録
      final data = await ApiService.sendNaturalText(text);

      setState(() {
        _result = '''
✅ 通信成功！

🕒 開始: ${data.startTime}  
🕕 終了: ${data.endTime}  
🎯 目的: ${data.purpose}  
📌 ステータス: ${data.status}  
🔥 優先度: ${data.priorityScore}
''';
      });

//       // 🧪 テスト用：FastAPIがFlutterから受け取るだけのときはこちら👇
      
//       final testData = await ApiService.sendTestRequest(text);
//       setState(() {
//         _result = '''
// ✅ 通信成功！

// 📩 メッセージ: ${testData["message"]}  
// 📥 受信内容: ${testData["received_text"]}
// ''';
//       });
      

    } catch (e) {
      setState(() {
        _result = "❌ 通信エラー: $e";
      });
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token'); // ✅ トークン削除
    Navigator.pushReplacementNamed(context, '/'); // ✅ ログイン画面へ戻る
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
        title: const Text("GPU予約アプリ"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'ログアウト',
            onPressed: logout,
          ),
        ],
      ),
      body: SafeArea(
        child: GestureDetector(
          // 🧼 タップでキーボード閉じる
          onTap: () => FocusScope.of(context).unfocus(),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: _controller,
                  decoration: const InputDecoration(
                    labelText: "自然文で予約希望を入力してください",
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                  keyboardType: TextInputType.multiline,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: sendText,
                  child: const Text("予約リクエスト送信"),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ReservationListPage()),
                    );
                  },
                  child: const Text("予約一覧を表示"),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ConflictPage()),
                    );
                  },
                  child: const Text("拒否確認待ち一覧を表示"),
                ),

                const SizedBox(height: 16),
                Text(
                  _result,
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

