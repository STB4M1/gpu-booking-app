class Reservation {
  final int id;
  final DateTime startTime;
  final DateTime endTime;
  final String purpose;
  final String status;
  final double priorityScore;
  final String? serverName;

  Reservation({
    required this.id,
    required this.startTime,
    required this.endTime,
    required this.purpose,
    required this.status,
    required this.priorityScore,
    this.serverName,
  });

  factory Reservation.fromJson(Map<String, dynamic> json) {
    return Reservation(
      id: json['id'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      purpose: json['purpose'],
      status: json['status'],
      priorityScore: json['priority_score'].toDouble(),
      serverName: json['server_name'],
    );
  }
}
