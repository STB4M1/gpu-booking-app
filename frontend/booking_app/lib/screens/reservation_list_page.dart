import 'package:flutter/material.dart';
import '../models/reservation.dart';
import '../services/api_service.dart';

class ReservationListPage extends StatelessWidget {
  const ReservationListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("予約一覧")),
      body: FutureBuilder<List<Reservation>>(
        future: ApiService.fetchReservations(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("⚠️ エラー: ${snapshot.error}"));
          }
          final reservations = snapshot.data!;
          if (reservations.isEmpty) {
            return const Center(child: Text("📭 予約がありません"));
          }
          return ListView.builder(
            itemCount: reservations.length,
            itemBuilder: (context, index) {
              final r = reservations[index];
              return Card(
                margin: const EdgeInsets.all(8),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("🕒 ${r.startTime} ～ ${r.endTime}"),
                      Text("🎯 目的: ${r.purpose}"),
                      Text("📌 ステータス: ${r.status}"),
                      Text("🔥 優先度: ${r.priorityScore}"),
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
