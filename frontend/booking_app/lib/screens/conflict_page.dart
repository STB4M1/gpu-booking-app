import 'package:flutter/material.dart';
import '../models/reservation.dart';
import '../services/api_service.dart';

class ConflictPage extends StatefulWidget {
  const ConflictPage({super.key});

  @override
  State<ConflictPage> createState() => _ConflictPageState();
}

class _ConflictPageState extends State<ConflictPage> {
  late Future<List<Reservation>> _pendingReservations;

  @override
  void initState() {
    super.initState();
    _pendingReservations = ApiService.fetchPendingConflicts();
  }

  void _refreshList() {
    setState(() {
      _pendingReservations = ApiService.fetchPendingConflicts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("⛔ 拒否確認待ち予約")),
      body: FutureBuilder<List<Reservation>>(
        future: _pendingReservations,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text("エラー: ${snapshot.error}"));
          }

          final reservations = snapshot.data!;
          if (reservations.isEmpty) {
            return const Center(child: Text("現在、確認待ちの予約はありません 🙌"));
          }

          return ListView.builder(
            itemCount: reservations.length,
            itemBuilder: (context, index) {
              final r = reservations[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                elevation: 3,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  title: Text("📌 ${r.purpose}"),
                  subtitle: Text("🕒 ${r.startTime} 〜 ${r.endTime}"),
                  trailing: ElevatedButton(
                    onPressed: () async {
                      await ApiService.confirmCancelReservation(r.id);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("予約を承諾（拒否）しました")),
                      );
                      _refreshList(); // 更新
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.redAccent,
                    ),
                    child: const Text("承諾"),
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
