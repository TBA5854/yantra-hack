import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/risk_state.dart';

abstract class RiskRepository {
  Future<RiskState> getRiskState();
  Stream<RiskState> riskStateStream();
}

class MockRiskRepository implements RiskRepository {
  @override
  Future<RiskState> getRiskState() async {
    await Future.delayed(const Duration(milliseconds: 500));
    return _generateMockData();
  }

  @override
  Stream<RiskState> riskStateStream() async* {
    while (true) {
      await Future.delayed(const Duration(seconds: 5));
      yield _generateMockData();
    }
  }

  RiskState _generateMockData() {
    return const RiskState(
      riskScore: 74,
      riskLevel: 'Red',
      tcs: 0.82,
      windowState: 'PROVISIONAL',
      explanations: [
        'Peg deviation persistent',
        'Liquidity dropped 18%',
        'Volatility spike',
      ],
      stressBreakdown: {
        'peg': {'value': 85, 'trend': 'up'},
        'liquidity': {'value': 60, 'trend': 'down'},
      },
      chainData: {'chain': 'Arbitrum', 'finality': 'Tier 2'},
    );
  }
}

final riskRepositoryProvider = Provider<RiskRepository>((ref) {
  return MockRiskRepository();
});
