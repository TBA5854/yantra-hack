import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/risk_state.dart';
import '../models/chain_finality_data.dart';
import '../models/stress_factor.dart';
import '../models/risk_snapshot.dart';

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
    return RiskState(
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
        'peg': const StressFactor(
          value: 85,
          trend: 'up',
          rollingMean: 82,
          contributionPercent: 0.5,
          history: [80, 81, 82, 83, 84, 85, 85, 86, 85],
          description: 'Peg deviation > 1.5% for 4 consecutive hours.',
        ),
        'liquidity': const StressFactor(
          value: 60,
          trend: 'down',
          rollingMean: 65,
          contributionPercent: 0.3,
          history: [70, 68, 65, 62, 60, 58, 60],
          description: 'Curve pool imbalance leaning heavily to USDC.',
        ),
        'volatility': const StressFactor(
          value: 45,
          trend: 'stable',
          rollingMean: 45,
          contributionPercent: 0.2,
          history: [40, 42, 45, 45, 44, 45],
          description: 'Market volatility index within normal deviation.',
        ),
      },
      history: [
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 5)),
          riskScore: 60,
          confidence: 0.90,
        ),
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 4)),
          riskScore: 65,
          confidence: 0.88,
        ),
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 3)),
          riskScore: 70,
          confidence: 0.85,
          event: 'Peg Deviation Alert',
        ),
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 2)),
          riskScore: 72,
          confidence: 0.83,
        ),
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 1)),
          riskScore: 74,
          confidence: 0.82,
        ),
      ],
      chainData: {'chain': 'Arbitrum', 'finality': 'Tier 2'},
      finalityWeight: 0.85,
      crossChainConfidence: 0.92,
      completeness: 0.98,
      stalenessPenalty: 0.0,
      chainFinalityList: [
        ChainFinalityData(
          chain: 'Ethereum',
          confirmations: 12,
          tier: 'Tier 1',
          finalized: true,
          lastReorg: DateTime.parse('2023-10-27 10:00:00'),
          confidence: 0.99,
        ),
        ChainFinalityData(
          chain: 'Arbitrum',
          confirmations: 450,
          tier: 'Tier 2',
          finalized: true,
          lastReorg: DateTime.parse('2023-10-26 14:30:00'),
          confidence: 0.95,
        ),
        ChainFinalityData(
          chain: 'Optimism',
          confirmations: 320,
          tier: 'Tier 2',
          finalized: true,
          lastReorg: DateTime.parse('2023-10-27 09:15:00'),
          confidence: 0.94,
        ),
        ChainFinalityData(
          chain: 'Polygon',
          confirmations: 1200,
          tier: 'Tier 3',
          finalized: false,
          lastReorg: DateTime.parse('2023-10-27 10:05:00'),
          confidence: 0.88,
        ),
      ],
    );
  }
}

final riskRepositoryProvider = Provider<RiskRepository>((ref) {
  return MockRiskRepository();
});
