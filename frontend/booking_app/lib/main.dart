import 'package:flutter/material.dart';
import 'screens/booking_page.dart';

void main() {
  runApp(const BookingApp());
}

class BookingApp extends StatelessWidget {
  const BookingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GPU予約アプリ',
      theme: ThemeData(primarySwatch: Colors.deepPurple),
      home: const BookingPage(),
    );
  }
}
