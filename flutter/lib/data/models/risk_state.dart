import 'package:freezed_annotation/freezed_annotation.dart';
import 'chain_finality_data.dart';
import 'stress_factor.dart';
import 'risk_snapshot.dart';

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
    required Map<String, StressFactor> stressBreakdown,
    required List<RiskSnapshot> history,
    required Map<String, dynamic> chainData,
    // New fields
    required double finalityWeight,
    required double crossChainConfidence,
    required double completeness,
    required double stalenessPenalty,
    required List<ChainFinalityData> chainFinalityList,
  }) = _RiskState;

  factory RiskState.fromJson(Map<String, dynamic> json) =>
      _$RiskStateFromJson(json);
}
