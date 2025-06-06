import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  String message = "";

  Future<void> login() async {
    final response = await http.post(
      Uri.parse('https://bdf2-182-167-109-2.ngrok-free.app/auth/token'),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: {
        'username': usernameController.text,
        'password': passwordController.text,
      },
    );

    if (response.statusCode == 200) {
      final jsonResponse = jsonDecode(response.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', jsonResponse['access_token']);
      setState(() {
        message = "✅ ログイン成功！";
      });

      // 予約一覧ページへ遷移
      Navigator.pushReplacementNamed(context, '/booking'); 
    } else {
      setState(() {
        message = "❌ ログイン失敗...";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("ログイン")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: usernameController, decoration: const InputDecoration(labelText: "ユーザー名")),
            TextField(controller: passwordController, decoration: const InputDecoration(labelText: "パスワード"), obscureText: true),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: login, child: const Text("ログイン")),
            const SizedBox(height: 20),
            Text(message),
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/register');
              },
              child: const Text("▶ 新規登録はこちら", style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }
}


