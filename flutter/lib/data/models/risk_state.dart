import 'package:freezed_annotation/freezed_annotation.dart';

part 'risk_state.freezed.dart';
part 'risk_state.g.dart';

@freezed
class RiskState with _$RiskState {
  const factory RiskState({
    required int riskScore,
    required String riskLevel, // 'Green', 'Yellow', 'Red'
    required double tcs, // Total Confidence Score
    required String windowState, // 'OPEN', 'PROVISIONAL', 'FINAL'
    required List<String> explanations,
    required Map<String, dynamic> stressBreakdown,
    required Map<String, dynamic> chainData,
  }) = _RiskState;

  factory RiskState.fromJson(Map<String, dynamic> json) =>
      _$RiskStateFromJson(json);
}
