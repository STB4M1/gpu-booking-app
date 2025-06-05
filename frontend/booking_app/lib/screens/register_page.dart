import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  String message = "";

Future<void> register() async {
  final response = await http.post(
    Uri.parse('https://fb3d-182-167-109-2.ngrok-free.app/auth/register'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': usernameController.text,
      'password': passwordController.text,
    }),
  );

  if (response.statusCode == 200) {
    setState(() {
      message = "✅ 登録成功！ログインしてね";
    });

    Future.delayed(const Duration(seconds: 1), () {
      Navigator.pushReplacementNamed(context, '/');
    });
  } else {
    // 👇 ここを修正
    final responseJson = jsonDecode(utf8.decode(response.bodyBytes));
    final detail = responseJson['detail'] ?? "サーバーエラーが発生しました";

    setState(() {
      message = "❌ 登録失敗: $detail";
    });
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("新規登録")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: usernameController, decoration: const InputDecoration(labelText: "ユーザー名")),
            TextField(controller: passwordController, decoration: const InputDecoration(labelText: "パスワード"), obscureText: true),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: register, child: const Text("登録")),
            const SizedBox(height: 20),
            Text(message),
          ],
        ),
      ),
    );
  }
}
