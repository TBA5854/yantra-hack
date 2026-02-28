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
    required String
    riskLevel, // 'MINIMAL', 'LOW', 'ELEVATED', 'HIGH', 'CRITICAL'
    required double tcs, // Total Confidence Score
    required String windowState, // 'OPEN', 'CLOSED', 'FINAL'
    required List<String> explanations,
    required Map<String, StressFactor> stressBreakdown,
    required List<RiskSnapshot> history,
    required Map<String, dynamic> chainData,
    // TCS breakdown fields
    required double finalityWeight,
    required double crossChainConfidence,
    required double completeness,
    required double stalenessPenalty,
    required List<ChainFinalityData> chainFinalityList,

    // ML-specific fields
    required String riskRating, // 'AAA', 'AA', 'A', 'B', 'C'
    @Default(false) bool mlEnabled,
    Map<String, dynamic>? models, // ISO + XGB outputs
    Map<String, dynamic>? explainability, // SHAP feature contributions
  }) = _RiskState;

  factory RiskState.fromJson(Map<String, dynamic> json) =>
      _$RiskStateFromJson(json);
}
