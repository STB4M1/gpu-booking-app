import 'package:flutter/material.dart';
import 'screens/booking_page.dart';
import 'screens/login_page.dart';
import 'screens/register_page.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

void main()async {
  await dotenv.load();
  runApp(const BookingApp());
}

class BookingApp extends StatelessWidget {
  const BookingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GPU予約アプリ',
      theme: ThemeData(primarySwatch: Colors.deepPurple),
      initialRoute: '/', // ← 最初に表示する画面
      routes: {
        '/': (context) => const LoginPage(),        // ログイン画面
        '/booking': (context) => const BookingPage(), // ログイン後の予約画面
        '/register': (context) => const RegisterPage(),
      },
    );
  }
}
