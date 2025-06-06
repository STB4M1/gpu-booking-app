import 'package:flutter/material.dart';
import '../models/reservation.dart';
import '../services/api_service.dart';

class ReservationListPage extends StatefulWidget {
  const ReservationListPage({super.key});

  @override
  State<ReservationListPage> createState() => _ReservationListPageState();
}

class _ReservationListPageState extends State<ReservationListPage> {
  late Future<List<Reservation>> _reservations;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  void _fetchData() {
    _reservations = ApiService.fetchReservations();
  }

  Color _getCardColor(String status) {
    switch (status) {
      case 'approved':
        return Colors.green.shade50; // 淡い緑
      case 'pending_conflict':
        return Colors.amber.shade50; // 淡いオレンジ 
      case 'rejected':
        return Colors.red.shade50; // 淡い赤
      default:
        return Colors.grey.shade100; // その他
    }
  }

  Future<void> _cancelReservation(int id) async {
    try {
      await ApiService.cancelReservation(id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("✅ 予約をキャンセルしました")),
      );
      setState(() => _fetchData()); // 更新
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("❌ キャンセル失敗: $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("予約一覧")),
      body: FutureBuilder<List<Reservation>>(
        future: _reservations,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("⚠️ エラー: ${snapshot.error}"));
          }

          final reservations = (snapshot.data!)
            .where((r) => r.status != 'cancelled' && r.status != 'rejected')
            .toList();
          if (reservations.isEmpty) {
            return const Center(child: Text("📭 予約がありません"));
          }

          return ListView.builder(
            itemCount: reservations.length,
            itemBuilder: (context, index) {
              final r = reservations[index];
              return Card(
                margin: const EdgeInsets.all(8),
                color: _getCardColor(r.status), // ← ここを追加！
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("🕒 ${r.startTime} ～ ${r.endTime}"),
                      Text("🎯 目的: ${r.purpose}"),
                      Text("📌 ステータス: ${r.status}"),
                      Text("🔥 優先度: ${r.priorityScore}"),
                      Text("🖥️ サーバー: ${r.serverName ?? "（未設定）"}"),
                      const SizedBox(height: 8),
                      if (r.status != "cancelled")
                        Align(
                          alignment: Alignment.centerRight,
                          child: ElevatedButton(
                            onPressed: () => _cancelReservation(r.id),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.redAccent,
                            ),
                            child: const Text("キャンセル"),
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
