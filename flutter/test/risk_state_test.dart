import 'package:flutter_test/flutter_test.dart';
import 'package:atlas/data/models/risk_state.dart';

void main() {
  test('RiskState model can be instantiated', () {
    const riskState = RiskState(
      riskScore: 74,
      riskLevel: 'Red',
      tcs: 0.82,
      windowState: 'PROVISIONAL',
      explanations: [],
      stressBreakdown: {},
      history: [],
      chainData: {},
      finalityWeight: 1.0,
      crossChainConfidence: 1.0,
      completeness: 1.0,
      stalenessPenalty: 0.0,
      chainFinalityList: [],
    );

    expect(riskState.riskScore, 74);
    expect(riskState.riskLevel, 'Red');
  });
}
