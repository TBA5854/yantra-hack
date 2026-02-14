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
      chainData: {},
    );

    expect(riskState.riskScore, 74);
    expect(riskState.riskLevel, 'Red');
  });
}
