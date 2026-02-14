import 'package:freezed_annotation/freezed_annotation.dart';

part 'risk_snapshot.freezed.dart';
part 'risk_snapshot.g.dart';

@freezed
class RiskSnapshot with _$RiskSnapshot {
  const factory RiskSnapshot({
    required DateTime timestamp,
    required int riskScore,
    required double confidence,
    String? event, // Optional event annotation
  }) = _RiskSnapshot;

  factory RiskSnapshot.fromJson(Map<String, dynamic> json) =>
      _$RiskSnapshotFromJson(json);
}
