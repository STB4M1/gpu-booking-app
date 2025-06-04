// import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:booking_app/main.dart';  // ← あなたのFlutterアプリをimport

void main() {
  testWidgets('GPU予約アプリが起動してタイトルが表示される', (WidgetTester tester) async {
    // アプリをビルド
    await tester.pumpWidget(BookingApp());

    // アプリバーのタイトルを確認
    expect(find.text('GPU予約アプリ'), findsOneWidget);
  });
}
